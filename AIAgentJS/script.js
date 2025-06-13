/*
Run this model in Javascript

> npm install @azure-rest/ai-inference @azure/core-auth @azure/core-sse
*/
import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";
import { AzureKeyCredential } from "@azure/core-auth";

// To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings. 
// Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
const token = "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";

export async function main() {
    const client = ModelClient(
        "https://models.github.ai/inference",
        new AzureKeyCredential(token)
    );

    const response = await client.path("/chat/completions").post({
        body: {
            messages: [
                { role: "user", content: "what 5 + 5?" }
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
