import asyncio
import ctypes
import logging
import os
import signal
import socket
import subprocess
import time
from typing import Any, Dict, List, Union

import requests
from openai import AsyncOpenAI, AuthenticationError
from openai._utils._logs import httpx_logger
from tqdm import tqdm

from fastmcp.exceptions import ToolError
from ultrarag.server import UltraRAG_MCP_Server

libc = ctypes.CDLL(None)
app = UltraRAG_MCP_Server("generation")
httpx_logger.setLevel(logging.WARNING)


def _is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def _set_pdeathsig():
    libc.prctl(1, signal.SIGTERM)


def _wait_for_vllm_ready(base_url: str, timeout: int, api_key: str):
    app.logger.info(f"Waiting for vLLM service at {base_url} to be ready...")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    for _ in range(timeout):
        try:
            resp = requests.get(f"{base_url}/models", headers=headers, timeout=2)
            if resp.status_code == 200:
                app.logger.info("vLLM service is ready.")
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)

    raise TimeoutError(
        f"vLLM service at {base_url} did not start within {timeout} seconds."
    )


@app.tool(output="model_path,model_name,port,gpu_ids,api_key->base_url")
def initialize_local_vllm(
    model_path: str,
    model_name: str,
    port: int,
    gpu_ids: str | int,
    api_key: str,
) -> Dict[str, str]:
    if _is_port_in_use(port):
        raise RuntimeError(
            f"Port {port} is already in use. Please choose another port."
        )
    gpu_ids = str(gpu_ids).strip()
    command = [
        "vllm",
        "serve",
        model_path,
        "--served-model-name",
        model_name,
        "--port",
        str(port),
        "--tensor-parallel-size",
        str(len(gpu_ids.split(","))),
        "--disable-log-requests",
        "--trust-remote-code",
    ]
    if api_key:
        command += ["--api-key", api_key]

    env = dict(**os.environ)
    env["CUDA_VISIBLE_DEVICES"] = gpu_ids

    app.logger.info(f"Starting vLLM model on GPU(s): {gpu_ids}")
    subprocess.Popen(command, env=env, preexec_fn=_set_pdeathsig)

    base_url = f"http://localhost:{port}/v1"
    timeout = 999
    _wait_for_vllm_ready(base_url, timeout, api_key)
    app.logger.info(f"vLLM service started at {base_url}")
    return {"base_url": base_url}


@app.tool(output="prompt_ls,model_name,base_url,sampling_params->ans_ls")
async def generate(
    prompt_ls: List[Union[str, Dict[str, Any]]],
    model_name: str,
    base_url: str,
    sampling_params: Dict[str, Any],
) -> Dict[str, List[str]]:
    api_key = os.environ.get("LLM_API_KEY", "")
    client = AsyncOpenAI(base_url=base_url, api_key=api_key if api_key else "EMPTY")

    prompts = []
    for m in prompt_ls:
        if hasattr(m, "content") and hasattr(m.content, "text"):
            prompts.append(m.content.text)
        elif isinstance(m, dict):
            prompts.append(m.get("content", {}).get("text", ""))
        elif isinstance(m, str):
            prompts.append(m)
        else:
            raise ValueError(f"Unsupported message format: {m}")

    sem = asyncio.Semaphore(64)

    async def call_with_retry(idx: int, prompt: str, retries=3, delay=1):
        msg = [{"role": "user", "content": prompt}]
        async with sem:
            for attempt in range(retries):
                try:
                    resp = await client.chat.completions.create(
                        model=model_name,
                        messages=msg,
                        **sampling_params,
                    )
                    return idx, resp.choices[0].message.content
                except AuthenticationError as e:
                    raise ToolError(
                        f"Unauthorized (401): Access denied at {base_url}."
                        "Invalid or missing LLM_API_KEY."
                    ) from e
                except Exception as e:
                    app.logger.warning(f"[Retry {attempt+1}] Failed (idx={idx}): {e}")
                    await asyncio.sleep(delay)
            return idx, "[ERROR]"

    tasks = [asyncio.create_task(call_with_retry(i, p)) for i, p in enumerate(prompts)]
    ret = [None] * len(prompts)

    for coro in tqdm(
        asyncio.as_completed(tasks), total=len(tasks), desc="Generating: "
    ):
        idx, ans = await coro
        ret[idx] = ans

    return {"ans_ls": ret}


if __name__ == "__main__":
    app.run(transport="stdio")
