import unittest
from unittest.mock import patch, MagicMock

from hermes_app.agent.loop import AgentLoop, OpenAI

class TestChatCommands(unittest.TestCase):
    @patch('hermes_app.agent.loop.OpenAI')
    def test_list_files_command(self, mock_openai):
        # Create an instance of the agent loop
        agent_loop = AgentLoop()

        # Mock the tool call response
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "list_files"
        mock_tool_call.function.arguments = '{"path": "src/hermes_app"}'
        mock_tool_call.id = "call_123"
        
        mock_choice = MagicMock()
        mock_choice.message.tool_calls = [mock_tool_call]
        mock_choice.message.content = None
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        # Configure the mock to return the mock response
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        mock_text_choice = MagicMock()
        mock_text_choice.message.tool_calls = None
        mock_text_choice.message.content = "Okay, I have the file list."

        mock_text_response = MagicMock()
        mock_text_response.choices = [mock_text_choice]

        # Configure the mock to return the tool response first, then the text response
        mock_openai.return_value.chat.completions.create.side_effect = [
            mock_response,
            mock_text_response,
        ]
        
        # Call the agent loop with the chat message
        agent_loop.chat("list files in src/hermes_app")

        # Check that the create method was called twice
        self.assertEqual(mock_openai.return_value.chat.completions.create.call_count, 2)

if __name__ == '__main__':
    unittest.main()
