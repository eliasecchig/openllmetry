import openai
import pytest


@pytest.mark.vcr
def test_embeddings(exporter, openai_client):
    openai_client.embeddings.create(
        input="Tell me a joke about opentelemetry",
        model="text-embedding-ada-002",
    )

    spans = exporter.get_finished_spans()
    assert [span.name for span in spans] == [
        "openai.embeddings",
    ]
    open_ai_span = spans[0]
    assert (
        open_ai_span.attributes["gen_ai.prompt.0.content"]
        == "Tell me a joke about opentelemetry"
    )
    assert open_ai_span.attributes["gen_ai.request.model"] == "text-embedding-ada-002"
    assert open_ai_span.attributes["gen_ai.usage.prompt_tokens"] == 8
    assert open_ai_span.attributes["openai.api_base"] == "https://api.openai.com/v1/"


@pytest.mark.vcr
def test_embeddings_with_raw_response(exporter, openai_client):
    response = openai_client.embeddings.with_raw_response.create(
        input="Tell me a joke about opentelemetry",
        model="text-embedding-ada-002",
    )
    spans = exporter.get_finished_spans()
    assert [span.name for span in spans] == [
        "openai.embeddings",
    ]
    open_ai_span = spans[0]
    assert (
        open_ai_span.attributes["gen_ai.prompt.0.content"]
        == "Tell me a joke about opentelemetry"
    )

    assert open_ai_span.attributes["gen_ai.request.model"] == "text-embedding-ada-002"
    assert open_ai_span.attributes["gen_ai.usage.prompt_tokens"] == 8
    assert open_ai_span.attributes["openai.api_base"] == "https://api.openai.com/v1/"

    parsed_response = response.parse()
    assert parsed_response.data[0]


@pytest.mark.vcr
def test_azure_openai_embeddings(exporter):
    api_key = "test-api-key"
    azure_resource = "test-resource"
    azure_deployment = "test-deployment"

    openai_client = openai.AzureOpenAI(
        api_key=api_key,
        azure_endpoint=f"https://{azure_resource}.openai.azure.com",
        azure_deployment=azure_deployment,
        api_version="2023-07-01-preview",
    )
    openai_client.embeddings.create(
        input="Tell me a joke about opentelemetry",
        model="embedding",
    )

    spans = exporter.get_finished_spans()
    assert [span.name for span in spans] == [
        "openai.embeddings",
    ]
    open_ai_span = spans[0]
    assert (
        open_ai_span.attributes["gen_ai.prompt.0.content"]
        == "Tell me a joke about opentelemetry"
    )
    assert open_ai_span.attributes["gen_ai.request.model"] == "embedding"
    assert open_ai_span.attributes["gen_ai.usage.prompt_tokens"] == 8
    assert (
        open_ai_span.attributes["openai.api_base"]
        == f"https://{azure_resource}.openai.azure.com/openai/deployments/{azure_deployment}/"
    )
    assert open_ai_span.attributes["openai.api_version"] == "2023-07-01-preview"
