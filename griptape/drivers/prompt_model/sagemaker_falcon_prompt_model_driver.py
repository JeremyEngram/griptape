from __future__ import annotations
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack, import_optional_dependency
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import BaseTokenizer, HuggingFaceTokenizer


@define
class SageMakerFalconPromptModelDriver(BasePromptModelDriver):
    _tokenizer: HuggingFaceTokenizer = field(default=None, kw_only=True)

    @property
    def tokenizer(self) -> HuggingFaceTokenizer:
        if self._tokenizer is None:
            self._tokenizer = HuggingFaceTokenizer(
                tokenizer=import_optional_dependency("transformers").AutoTokenizer.from_pretrained(
                    "tiiuae/falcon-40b", model_max_length=self.max_tokens
                )
            )
        return self._tokenizer

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> str:
        return self.prompt_driver.prompt_stack_to_string(prompt_stack)

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_model_input(prompt_stack)
        stop_sequences = self.prompt_driver.tokenizer.stop_sequences

        return {
            "max_new_tokens": self.prompt_driver.max_output_tokens(prompt),
            "temperature": self.prompt_driver.temperature,
            "do_sample": True,
            "stop": stop_sequences,
        }

    def process_output(self, output: list[dict] | str | bytes) -> TextArtifact:
        if isinstance(output, list):
            return TextArtifact(output[0]["generated_text"].strip())
        else:
            raise ValueError("output must be an instance of 'list'")
