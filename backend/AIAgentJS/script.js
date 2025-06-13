/*
Run this model in Javascript

> npm install @azure-rest/ai-inference @azure/core-auth @azure/core-sse
*/
import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";
import { AzureKeyCredential } from "@azure/core-auth";
import dotenv from "dotenv";


dotenv.config();
const token = process.env.GITHUB_TOKEN;

export async function main() {
    const client = ModelClient(
        "https://models.github.ai/inference",
        new AzureKeyCredential(token)
    );

    const response = await client.path("/chat/completions").post({
        body: {
            messages: [
                { role: "user", content: "Tell me about Fifa world club cup 2025?" }
            ],
            model: "deepseek/DeepSeek-R1",
            max_tokens: 2048,
        }
    });

    if (isUnexpected(response)) {
        throw response.body.error;
    }
    console.log(response.body.choices[0].message.content);
}

main().catch((err) => {
    console.error("The sample encountered an error:", err);
});
