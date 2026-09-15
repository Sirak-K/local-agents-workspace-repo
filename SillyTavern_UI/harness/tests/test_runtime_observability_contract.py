from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
KOBOLD = (ROOT / 'Start-KoboldCpp-StorytellerRuntime.ps1').read_text(encoding='utf-8')
SILLY = (ROOT / 'Start-SillyTavern.ps1').read_text(encoding='utf-8')
PROBE = (ROOT / 'Test-KoboldCpp-StorytellerChatProfile.ps1').read_text(encoding='utf-8')
MODULE = (ROOT / 'RuntimeObservability.psm1').read_text(encoding='utf-8')

class RuntimeObservabilityContractTests(unittest.TestCase):
    def test_kobold_launch_flags_and_profiles_are_preserved(self):
        for token in (
            "'--model', $model", "'--host', '127.0.0.1'", "'--port', \"$Port\"",
            "'--contextsize', \"$ContextSize\"", "'--usecuda', 'normal', \"$GpuId\"",
            "'--gpulayers', '-1'", "'--nommq'", "'--highpriority'", "'--quantkv', 'f16'", "'--noswa'",
            "$KoboldArgs += '--jinjathink'", "$KoboldArgs += 'false'", "$KoboldArgs += '--mmproj'",
        ):
            with self.subTest(token=token): self.assertIn(token, KOBOLD)
        self.assertIn('& $exe @KoboldArgs', KOBOLD)
        self.assertIn('Start-Process -FilePath $exe -ArgumentList $argumentLine -PassThru -WindowStyle Hidden', KOBOLD)

    def test_sillytavern_launch_contract_is_preserved(self):
        self.assertIn("$argumentLine = '/k \"{0}\"' -f $StartBat", SILLY)
        self.assertIn('Start-Process -FilePath $cmdExe -ArgumentList $argumentLine -WorkingDirectory $SillyDir -PassThru', SILLY)
        self.assertIn("-Owner 'sillytavern'", SILLY)

    def test_probe_contract_and_validation_are_preserved(self):
        self.assertIn("content = 'Reply with exactly STORYTELLER_PROFILE_OK and nothing else.'", PROBE)
        self.assertIn("-Uri \"$base/v1/chat/completions\"", PROBE)
        self.assertIn("Test-StorytellerChatResponseContract -Response $response -ExpectedContent $expectedContent", PROBE)
        self.assertIn("Get-JsonEndpoint '/api/extra/perf'", PROBE)
        self.assertIn("'X-Local-Agents-Correlation-Id' = $CorrelationId", PROBE)

    def test_default_runtime_log_does_not_add_raw_request_or_response(self):
        self.assertIn("if ($LogRawIO) { $requestDetails['content'] = $requestJson }", PROBE)
        self.assertIn("if ($LogRawIO) { $responseDetails['content'] = $responseJson }", PROBE)
        self.assertIn('-AllowSensitiveContent:$LogRawIO', PROBE)
        self.assertNotRegex(PROBE, r"requestDetails\s*=\s*@\{[^}]*content\s*=")
        self.assertNotRegex(PROBE, r"responseDetails\s*=\s*@\{[^}]*content\s*=")

    def test_observability_module_is_best_effort_and_uses_project_root(self):
        self.assertIn("Join-Path $script:ProjectRoot '.venv\\Scripts\\python.exe'", MODULE)
        self.assertIn('Push-Location $script:ProjectRoot', MODULE)
        self.assertIn('return $null', MODULE)
        self.assertIn('-m runtime_logging', MODULE)

    def test_owner_boundaries_are_not_collapsed(self):
        self.assertIn("-Owner 'sillytavern'", SILLY)
        self.assertIn("-Owner 'koboldcpp'", KOBOLD)
        self.assertIn("-Owner 'koboldcpp'", PROBE)
        self.assertNotIn("-Owner 'runtime'", SILLY + KOBOLD + PROBE)

if __name__ == '__main__':
    unittest.main()
