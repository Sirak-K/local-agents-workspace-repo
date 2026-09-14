import { readFile } from "node:fs/promises";
import { LMStudioClient } from "../../LM-Studio_connections/LM-Studio_for_codex/node_modules/@lmstudio/sdk/dist/index.mjs";
import { authenticatedOptions } from "../../LM-Studio_connections/LM-Studio_for_codex/lm_studio_sdk_prediction.mjs";

const client = new LMStudioClient(authenticatedOptions(process.env.LM_API_TOKEN, "ws://127.0.0.1:1234"));
try {
  const model = (await client.llm.listLoaded()).find(item => item.identifier === "qwen2.5-7b-instruct");
  if (!model) throw new Error("selected_model_not_loaded");
  const body = await readFile("model_evaluations/comfy_ui_eval-playground/source_snapshots/workflow_reference.json", "utf8");
  console.log(JSON.stringify({ workflow_bytes: Buffer.byteLength(body, "utf8"), workflow_tokens: await model.countTokens(body), context_length: (await model.getModelInfo()).contextLength }));
} finally {
  await client[Symbol.asyncDispose]();
}
