import importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('dns',str(Path(__file__).resolve().parents[1] / 'scripts' / 'point-beget-dns-to-github-pages.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DnsTests(unittest.TestCase):
 def entry(self,**kw):return dict(fqdn=m.WWW,is_beget_dns=True,is_subdomain=True,set_type=1,records={},**kw)
 def test_correct_public_alias_needs_no_api_write(self):
  with patch.object(m,'public_www_cname',return_value=[m.WWW_TARGET]),patch.object(m,'call') as call:
   m.ensure_www();call.assert_not_called()
 def test_stale_alias_updates_only_www(self):
  with patch.object(m,'public_www_cname',return_value=[]),patch.object(m,'call',side_effect=[self.entry(),True]) as call:
   m.ensure_www();self.assertEqual(call.call_args.args,('changeRecords',{'fqdn':m.WWW,'records':{'CNAME':[{'priority':10,'value':m.WWW_TARGET}]}}))
 def test_mail_is_never_deleted(self):
  e=self.entry();e['records']={'MX':[{'value':'mail.example.com','priority':10}]}
  with patch.object(m,'public_www_cname',return_value=[]),patch.object(m,'call',return_value=e) as call:
   with self.assertRaisesRegex(RuntimeError,'mail/TXT'):m.ensure_www()
   self.assertEqual(call.call_count,1)
 def test_wrong_domain_is_never_written(self):
  e=self.entry();e['fqdn']='other.example.com'
  with patch.object(m,'public_www_cname',return_value=[]),patch.object(m,'call',return_value=e) as call:
   with self.assertRaisesRegex(RuntimeError,'wrong www'):m.ensure_www()
   self.assertEqual(call.call_count,1)
 def test_missing_www_is_created_only_under_exact_parent(self):
  with patch.object(m,'public_www_cname',return_value=[]),patch.object(m,'call',side_effect=[RuntimeError('Beget DNS request rejected: getData METHOD_FAILED'),[],[{'fqdn':m.DOMAIN,'id':'123'}],'456',self.entry(),True]) as call:
   m.ensure_www()
   self.assertEqual(call.call_args_list[3].args,('addSubdomainVirtual',{'subdomain':'www','domain_id':123}))
   self.assertEqual(call.call_args_list[3].kwargs,{'section':'domain'})
 def test_unreadable_existing_www_is_not_recreated(self):
  with patch.object(m,'public_www_cname',return_value=[]),patch.object(m,'call',side_effect=[RuntimeError('Beget DNS request rejected: getData METHOD_FAILED'),[{'fqdn':m.WWW}]]) as call:
   with self.assertRaisesRegex(RuntimeError,'exists but'):m.ensure_www()
   self.assertEqual(call.call_count,2)
if __name__=='__main__':unittest.main()
