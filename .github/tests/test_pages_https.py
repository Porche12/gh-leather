#!/usr/bin/env python3
"""Network-free regression checks for safe Pages/TLS remediation."""
import importlib.util
import io
from pathlib import Path
import ssl
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ensure-pages-https.py"
spec = importlib.util.spec_from_file_location("pages_https", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PagesFlowTests(unittest.TestCase):
    def test_refresh_keeps_domain_attached_and_enables_https(self):
        client = MagicMock()
        client.call.side_effect = [
            {"cname": module.DOMAIN}, None, {"cname": module.DOMAIN},
            None, {"cname": module.DOMAIN, "https_enforced": True},
        ]
        module.configure_https(client)
        actual = [call.args for call in client.call.call_args_list]
        self.assertEqual(actual, [
            ("GET",), ("PUT", {"cname": module.DOMAIN}), ("GET",),
            ("PUT", {"https_enforced": True}), ("GET",),
        ])
        self.assertFalse(any(args[0] == "DELETE" for args in actual))

    def test_unexpected_domain_never_mutated(self):
        for cname in (None, "", "someone-else.ru", "www.ghleather.ru"):
            with self.subTest(cname=cname):
                client = MagicMock()
                client.call.return_value = {"cname": cname}
                with self.assertRaises(module.VerificationError):
                    module.configure_https(client)
                self.assertEqual(client.call.call_count, 1)

    def test_changed_domain_after_refresh_stops_enforcement(self):
        client = MagicMock()
        client.call.side_effect = [{"cname": module.DOMAIN}, None, {"cname": None}]
        with self.assertRaises(module.VerificationError):
            module.configure_https(client)
        self.assertEqual(client.call.call_count, 3)

    def test_unconfirmed_enforcement_fails(self):
        client = MagicMock()
        client.call.side_effect = [
            {"cname": module.DOMAIN}, None, {"cname": module.DOMAIN},
            None, {"cname": module.DOMAIN, "https_enforced": False},
        ]
        with self.assertRaisesRegex(module.VerificationError, "not confirmed"):
            module.configure_https(client)

    def test_422_pending_failure_does_not_log_response_or_token(self):
        client = module.GitHubPagesClient("Porche12/gh-leather", "SECRET_TOKEN_TEST")
        error = urllib.error.HTTPError(client.url, 422, "private API detail", {}, io.BytesIO(b"SECRET_TOKEN_TEST PRIVATE_BODY"))
        with patch.object(module.urllib.request, "urlopen", side_effect=error):
            with self.assertRaisesRegex(module.VerificationError, "certificate may still be pending") as result:
                client.call("PUT", {"https_enforced": True})
        self.assertNotIn("SECRET_TOKEN_TEST", str(result.exception))
        self.assertNotIn("PRIVATE_BODY", str(result.exception))
        self.assertNotIn("private API detail", str(result.exception))

    def test_failed_configuration_never_claims_origin_pass(self):
        with patch.object(module, "GitHubPagesClient"), patch.object(module, "configure_https", side_effect=module.VerificationError("pending")), patch.object(module, "verify_live_site") as live:
            with self.assertRaises(module.VerificationError):
                module.main()
            live.assert_not_called()


class OriginTests(unittest.TestCase):
    def test_http_redirects_to_canonical_https(self):
        with patch.object(module, "request_status", side_effect=[(301, "https://ghleather.ru/"), (200, None)]):
            module.verify_redirect_chain("http://ghleather.ru/", require_redirect=True)

    def test_www_can_use_two_canonical_redirects(self):
        with patch.object(module, "request_status", side_effect=[(301, "https://www.ghleather.ru/"), (301, "https://ghleather.ru/"), (200, None)]):
            module.verify_redirect_chain("http://www.ghleather.ru/", require_redirect=True)

    def test_insecure_200_fails(self):
        with patch.object(module, "request_status", return_value=(200, None)):
            with self.assertRaises(module.VerificationError):
                module.verify_redirect_chain("http://ghleather.ru/", require_redirect=True)

    def test_https_downgrade_and_foreign_redirect_fail(self):
        for destination in ("http://ghleather.ru/", "https://example.com/"):
            with self.subTest(destination=destination), patch.object(module, "request_status", return_value=(301, destination)):
                with self.assertRaises(module.VerificationError):
                    module.verify_redirect_chain("https://www.ghleather.ru/", require_redirect=True)

    def test_redirect_loop_fails(self):
        with patch.object(module, "request_status", return_value=(301, "/")):
            with self.assertRaisesRegex(module.VerificationError, "loop"):
                module.verify_redirect_chain("http://ghleather.ru/", require_redirect=True)

    def test_bad_certificate_never_falls_back_to_http(self):
        context = MagicMock()
        context.wrap_socket.side_effect = ssl.SSLCertVerificationError("wrong certificate")
        with patch.object(module.ssl, "create_default_context", return_value=context), patch.object(module.socket, "create_connection"):
            with self.assertRaisesRegex(module.VerificationError, "hostname or validity"):
                module.verify_tls_host("ghleather.ru")
        self.assertEqual(context.wrap_socket.call_args.kwargs["server_hostname"], "ghleather.ru")

    def test_tls_checks_both_hosts_and_all_entry_points(self):
        with patch.object(module, "verify_tls_host") as tls, patch.object(module, "verify_redirect_chain") as redirect:
            module.verify_live_site()
        self.assertEqual([call.args[0] for call in tls.call_args_list], ["ghleather.ru", "www.ghleather.ru"])
        self.assertEqual(redirect.call_count, 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
