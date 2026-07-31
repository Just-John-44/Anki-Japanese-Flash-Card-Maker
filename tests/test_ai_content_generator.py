# test_ai_content_generator.py
# Created: Jul 29 2026
# Last Edited: Jul 30 2026
# Author: John Wesley Thompson

from createcards.ai_content_generator import IDEOGRAPHIC_SPACE, OpenAIContentGenerator
from createcards.ccnote import Word
import json
import pytest
from types import SimpleNamespace

# AI Content Generator Requirements
# Raise Exceptions If -----
# - Client initialization fails (should be handled already by the OpenAI API)
# - Request runtime fails
# - Malformed responses
# - Invalid Word list input

def make_mock_client(completion_response, mocker, encode_json=True):
    mock = mocker.Mock()
    mock.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=json.dumps(completion_response) if encode_json else completion_response
                )
            )
        ]
    )
    return mock


# -----------------------------------------------------------------------------
# DEPENDENCY TESTING
# -----------------------------------------------------------------------------

def test_missing_api_key(mocker, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mock_openai_client = make_mock_client("doesn't matter", mocker)
    with pytest.raises(RuntimeError):
        OpenAIContentGenerator(client=mock_openai_client)

# -----------------------------------------------------------------------------
# OUTPUT TESTING
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "completion_response, expected_sentences, expected_tags",
    [
        (
            {
                f"犬{IDEOGRAPHIC_SPACE}いぬ": {
                    "s1": "彼は犬を飼っています。",
                    "s2": "大きな犬がすきです。",
                    "tags": "Neutral・Common・Daily Life",
                }
            },
            [
                "彼は犬を飼っています。<br>大きな犬がすきです。",
            ],
            [
                "Neutral・Common・Daily Life",
            ],
        ),
    ],
)
def test_generate_content_success(
    completion_response,
    expected_sentences,
    expected_tags,
    mocker,
    monkeypatch
):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mock_openai_client = make_mock_client(completion_response, mocker)

    ai_content_generator = OpenAIContentGenerator(client=mock_openai_client)
    words = [Word("犬", "いぬ")]
    sentences, tags = ai_content_generator.generate_content(words)

    assert sentences == expected_sentences
    assert tags == expected_tags


def test_generate_content_json_decode_failure(mocker, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mock_openai_client = make_mock_client("invalid json", mocker, encode_json=False)
    ai_content_generator = OpenAIContentGenerator(client=mock_openai_client)

    words = [Word("犬", "いぬ")] # Fixed because only predetermined output is being tested
    with pytest.raises(json.JSONDecodeError):
        ai_content_generator.generate_content(words)


@pytest.mark.parametrize(
    "completion_response, expected_exception",
    [
        ( # Not a json object
            [
                {
                    f"犬{IDEOGRAPHIC_SPACE}いぬ": {
                        "s1": "彼は犬を飼っています。",
                        "s2": "大きな犬がすきです。",
                        "tags": "Neutral・Common・Daily Life",
                    }
                }
            ],
            ValueError
        ),
        ( # Not a json object
            """
                "犬 いぬ": {
                    "s1": "彼は犬を飼っています。",
                    "s2": "大きな犬がすきです。",
                    "tags": "Neutral・Common・Daily Life",
                }
            """,
            ValueError
        ),
        (
            { # Missing "s1" or "s2"
                f"犬{IDEOGRAPHIC_SPACE}いぬ": {
                    "s1": "彼は犬を飼っています。",
                    "tags": "Neutral・Common・Daily Life",
                }
            },
            KeyError
        ),
        (
            { # Missing "tags"
                f"犬{IDEOGRAPHIC_SPACE}いぬ": {
                    "s1": "彼は犬を飼っています。",
                    "s2": "大きな犬がすきです。",
                }
            },
            KeyError
        ),
    ],
)
def test_generate_content_invalid_json_response(
    completion_response,
    expected_exception,
    mocker,
    monkeypatch
):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mock_openai_client = make_mock_client(completion_response, mocker)
    ai_content_generator = OpenAIContentGenerator(client=mock_openai_client)

    words = [Word("犬", "いぬ")]
    with pytest.raises(expected_exception):
        ai_content_generator.generate_content(words)


def test_missing_output_failure(
    mocker,
    monkeypatch,
):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mock_openai_client = make_mock_client(
        {
            f"犬{IDEOGRAPHIC_SPACE}いぬ": {
                "s1": "彼は犬を飼っています。",
                "s2": "大きな犬がすきです。",
                "tags": "Neutral・Common・Daily Life",
            }
        },
        mocker
    )
    ai_conent_generator = OpenAIContentGenerator(client=mock_openai_client)

    with pytest.raises(RuntimeError):
        ai_conent_generator.generate_content([Word("犬", "いぬ"), Word("猫", "ねこ")])


# -----------------------------------------------------------------------------
# INPUT TESTING
# -----------------------------------------------------------------------------

def test_empty_input(mocker, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mock_openai_client = make_mock_client(
        {}
        , mocker
    )
    ai_content_generator = OpenAIContentGenerator(client=mock_openai_client)
    with pytest.raises(ValueError):
        ai_content_generator.generate_content([])