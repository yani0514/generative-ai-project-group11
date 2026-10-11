"""Offline checks for the loop's protocol, caps, and tool boundary."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'starter'))
from agent import run_task, run_tool_call, SCHEMAS, MAX_RESULT_CHARS
from tasks import TASKS
from project.fixtures import _wrap


class Client:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.requests.append(json.loads(json.dumps(kwargs)))
        return _wrap(next(self.replies))


def reply(tool=None, content='', tokens=10):
    calls = [] if tool is None else [{
        'id': 'call_1', 'type': 'function',
        'function': {'name': tool[0], 'arguments': json.dumps(tool[1])}}]
    return {'choices': [{'message': {'content': content, 'tool_calls': calls}}],
            'usage': {'prompt_tokens': tokens, 'completion_tokens': 1}}


class LoopTests(unittest.TestCase):
    def run_agent(self, client, **kwargs):
        with patch('agent.TraceRecorder.finish'):
            return run_task(client, TASKS[0], **kwargs)

    def test_protocol_and_arithmetic(self):
        client = Client([reply(('search_services', {'query': 'waste fee'})),
                         reply(('compute', {'expression': '26 * 8.50 + 24'})),
                         reply(content='245 EUR')])
        run = self.run_agent(client)
        self.assertEqual(run.answer, '245 EUR')
        self.assertEqual(run.tool_calls, ['search_services', 'compute'])
        self.assertEqual(run.steps, 3)
        self.assertEqual(run.tokens, 33)
        messages = client.requests[1]['messages']
        self.assertEqual(messages[-2]['role'], 'assistant')
        self.assertEqual(messages[-1]['tool_call_id'], 'call_1')
        self.assertIsNone(run.cap_fired)

    def test_all_caps(self):
        call = reply(('search_services', {'query': 'waste fee'}))
        for kwargs, replies, expected in [
                ({'max_steps': 1}, [call], 'steps'),
                ({'max_tokens_budget': 1}, [call], 'budget'),
                ({'stall_limit': 2}, [call] * 3, 'no_progress')]:
            run = self.run_agent(Client(replies), **kwargs)
            self.assertEqual(run.cap_fired, expected)
            self.assertTrue(run.answer)
            self.assertIn(expected, run.answer)

    def test_no_tools(self):
        client = Client([reply(content='translation')])
        self.run_agent(client, no_tools=True)
        self.assertNotIn('tools', client.requests[0])

    def test_tool_errors_and_output_bound(self):
        for name, args in [('compute', '{'), ('unknown', '{}'),
                           ('compute', '[]'), ('compute', '{}'),
                           ('search_services', '{"query":"x","top_k":true}'),
                           ('compute', '{"expression":"1 / 0"}')]:
            self.assertTrue(run_tool_call(name, args)[1])
        with patch.dict('agent.DISPATCH', compute=lambda **_: (_ for _ in ()).throw(
                RuntimeError('/private/secret/file.py'))):
            result, error = run_tool_call('compute', '{"expression":"1"}')
            self.assertTrue(error)
            self.assertNotIn('/private', str(result))
        with patch.dict('agent.DISPATCH', compute=lambda **_: 'x' * 5000):
            result, error = run_tool_call('compute', '{"expression":"1"}')
            self.assertLessEqual(len(result), MAX_RESULT_CHARS)
        self.assertEqual(SCHEMAS[0]['type'], 'function')


if __name__ == '__main__':
    unittest.main()
