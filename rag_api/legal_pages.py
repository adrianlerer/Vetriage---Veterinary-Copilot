"""
Legal pages required by Paddle for merchant verification.
Served as HTML endpoints from the API itself.

Seller: Ignacio Adrian Lerer - CUIT 20-18285589-9
Jurisdiction: Argentina (Responsable Inscripto - ARCA)
Domain: vetriage.com.ar
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime

router = APIRouter(tags=["Legal"])

COMPANY = "Ignacio Adrian Lerer"
CUIT = "20-18285589-9"
BRAND = "VetrIAge"
DOMAIN = "vetriage.com.ar"
CONTACT_EMAIL = "legal@vetriage.com.ar"
EFFECTIVE_DATE = "2025-07-01"

_CSS = """
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         max-width: 800px; margin: 40px auto; padding: 0 20px; color: #1a1a1a;
         line-height: 1.7; }
  h1 { color: #0f4c81; border-bottom: 2px solid #0f4c81; padding-bottom: 10px; }
  h2 { color: #0f4c81; margin-top: 2em; }
  .meta { color: #666; font-size: 0.9em; margin-bottom: 2em; }
  ul { padding-left: 1.5em; }
  .highlight { background: #f0f7ff; padding: 12px 16px; border-left: 4px solid #0f4c81;
               margin: 1em 0; border-radius: 4px; }
</style>
"""


@router.get("/terms", response_class=HTMLResponse)
async def terms_and_conditions():
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Terms & Conditions - {BRAND}</title>{_CSS}</head>
<body>
<h1>Terms &amp; Conditions</h1>
<p class="meta">Effective date: {EFFECTIVE_DATE} &middot; {BRAND} &middot; operated by {COMPANY} (CUIT {CUIT})</p>

<h2>1. Service Description</h2>
<p>{BRAND} provides an evidence-based veterinary diagnostic API ("the Service"). The Service uses retrieval-augmented generation (RAG) over PubMed, bioRxiv, and curated veterinary databases to deliver differential diagnoses, drug safety checks, and literature search results via a RESTful API.</p>

<h2>2. Acceptance</h2>
<p>By registering for an API key or making any API call to the Service, you ("the Customer") agree to these Terms &amp; Conditions. If you do not agree, do not use the Service.</p>

<h2>3. Account &amp; API Keys</h2>
<ul>
  <li>Each API key is personal and non-transferable.</li>
  <li>You are responsible for keeping your API key confidential.</li>
  <li>You must not share your API key or allow third parties to use it without written consent.</li>
  <li>We reserve the right to deactivate keys that violate these terms.</li>
</ul>

<h2>4. Permitted Use</h2>
<ul>
  <li>The Service is intended for licensed veterinary professionals, veterinary clinics, animal health researchers, and authorized software integrators.</li>
  <li>Outputs are decision-support tools and do not constitute veterinary medical advice. A licensed veterinarian must always make the final clinical decision.</li>
  <li>You must not use the Service for human medical diagnosis or treatment.</li>
</ul>

<h2>5. Subscription Plans &amp; Billing</h2>
<ul>
  <li>Plans are billed monthly through our payment processor, Paddle (Paddle.com Market Limited).</li>
  <li>Usage limits are enforced per calendar month and reset on the 1st of each month (UTC).</li>
  <li>Exceeding your plan's limits will result in HTTP 429 responses until the next billing cycle or until you upgrade.</li>
  <li>Prices are in USD and exclude applicable taxes, which Paddle collects as Merchant of Record.</li>
</ul>

<h2>6. Intellectual Property</h2>
<p>The Service, its algorithms, and documentation are owned by {COMPANY}. API outputs (diagnostic results, safety reports) may be used by the Customer in their clinical practice or integrated software, but the underlying system and models remain our property.</p>

<h2>7. Disclaimer &amp; Limitation of Liability</h2>
<div class="highlight">
<strong>Important:</strong> {BRAND} is a clinical decision-support tool, not a replacement for professional veterinary judgment. All diagnostic outputs should be reviewed by a licensed veterinarian before any clinical action is taken.
</div>
<ul>
  <li>THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND.</li>
  <li>We do not guarantee the accuracy, completeness, or clinical applicability of any output.</li>
  <li>In no event shall {COMPANY} be liable for any indirect, incidental, or consequential damages arising from use of the Service.</li>
  <li>Our total liability is limited to the fees paid by the Customer in the 3 months preceding the claim.</li>
</ul>

<h2>8. Data &amp; Privacy</h2>
<p>Your use of the Service is also governed by our <a href="/privacy">Privacy Policy</a>. Clinical case data submitted via the API is processed solely to generate diagnostic outputs and is not retained beyond the session unless explicitly opted in.</p>

<h2>9. Termination</h2>
<ul>
  <li>You may cancel your subscription at any time through Paddle's customer portal.</li>
  <li>We may suspend or terminate access for violation of these Terms, with notice where practicable.</li>
  <li>Upon termination, your API key is deactivated and usage data is retained for 90 days for billing reconciliation.</li>
</ul>

<h2>10. Modifications</h2>
<p>We may update these Terms with 30 days' notice via email to the address associated with your API key. Continued use after the notice period constitutes acceptance.</p>

<h2>11. Governing Law</h2>
<p>These Terms are governed by the laws of the Argentine Republic. Any disputes shall be submitted to the ordinary courts of the Autonomous City of Buenos Aires, Argentina.</p>

<h2>12. Refund Policy</h2>
<p>Please see our <a href="/refund-policy">Refund Policy</a> for details on cancellations and refunds.</p>

<h2>13. Contact</h2>
<p>{COMPANY}<br>CUIT: {CUIT}<br>Email: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</body></html>"""


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacy Policy - {BRAND}</title>{_CSS}</head>
<body>
<h1>Privacy Policy</h1>
<p class="meta">Effective date: {EFFECTIVE_DATE} &middot; {BRAND} &middot; operated by {COMPANY} (CUIT {CUIT})</p>

<h2>1. Data Controller</h2>
<p>{COMPANY}, CUIT {CUIT}, is the data controller for the {BRAND} API service. Contact: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

<h2>2. Data We Collect</h2>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%;">
<tr style="background:#f0f7ff;"><th>Category</th><th>Data</th><th>Purpose</th><th>Retention</th></tr>
<tr><td>Account</td><td>Email, name, API key hash</td><td>Authentication, billing</td><td>Duration of account + 90 days</td></tr>
<tr><td>Usage</td><td>Endpoint called, timestamp, response time, status code</td><td>Rate limiting, billing, analytics</td><td>12 months rolling</td></tr>
<tr><td>Clinical Input</td><td>Species, symptoms, lab results submitted via API</td><td>Generate diagnostic output</td><td>Not retained after response (ephemeral)</td></tr>
<tr><td>Payment</td><td>Handled entirely by Paddle</td><td>Subscription billing</td><td>Per Paddle's privacy policy</td></tr>
</table>

<h2>3. How We Use Your Data</h2>
<ul>
  <li><strong>Service delivery:</strong> Processing API requests and generating diagnostic outputs.</li>
  <li><strong>Billing:</strong> Tracking usage against plan limits.</li>
  <li><strong>Security:</strong> Detecting abuse, enforcing rate limits.</li>
  <li><strong>Improvement:</strong> Aggregated, anonymized usage statistics to improve the Service. No individual clinical data is used for training.</li>
</ul>

<h2>4. Clinical Data Processing</h2>
<div class="highlight">
<strong>We do not store clinical case data.</strong> Animal patient information submitted to the /diagnose or /safety-check endpoints is processed in-memory to generate the response and is discarded immediately after. No clinical data is written to disk, logged, or used for model training.
</div>

<h2>5. Third-Party Services</h2>
<ul>
  <li><strong>Paddle (Merchant of Record):</strong> Processes payments and manages subscriptions. See <a href="https://www.paddle.com/legal/privacy" target="_blank">Paddle's Privacy Policy</a>.</li>
  <li><strong>PubMed / NCBI:</strong> Literature searches query NCBI's public APIs. No customer data is sent to NCBI.</li>
  <li><strong>LLM Providers:</strong> Diagnostic inference uses third-party LLM APIs (OpenAI/Anthropic). Clinical data is sent to these providers for processing under their data processing agreements. No data is retained by these providers for training.</li>
  <li><strong>Render.com:</strong> Infrastructure hosting. See <a href="https://render.com/privacy" target="_blank">Render's Privacy Policy</a>.</li>
</ul>

<h2>6. Data Security</h2>
<ul>
  <li>API keys are stored as SHA-256 hashes — we cannot recover your raw key.</li>
  <li>All API traffic is encrypted via TLS 1.2+.</li>
  <li>Access to production systems is restricted to authorized personnel.</li>
</ul>

<h2>7. Your Rights</h2>
<p>Under Argentine data protection law (Ley 25.326) and international standards, you have the right to:</p>
<ul>
  <li>Access your personal data</li>
  <li>Request correction of inaccurate data</li>
  <li>Request deletion of your data ("right to be forgotten")</li>
  <li>Export your usage data</li>
</ul>
<p>To exercise these rights, email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

<h2>8. Cookies</h2>
<p>The API itself does not use cookies. If you access our documentation site, it may use essential cookies for functionality (no tracking cookies).</p>

<h2>9. Changes</h2>
<p>We will notify you of material changes to this policy via the email associated with your API key at least 14 days before they take effect.</p>

<h2>10. Contact</h2>
<p>{COMPANY}<br>CUIT: {CUIT}<br>Email: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</body></html>"""


@router.get("/refund-policy", response_class=HTMLResponse)
async def refund_policy():
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Refund Policy - {BRAND}</title>{_CSS}</head>
<body>
<h1>Refund Policy</h1>
<p class="meta">Effective date: {EFFECTIVE_DATE} &middot; {BRAND} &middot; operated by {COMPANY} (CUIT {CUIT})</p>

<h2>14-Day Money-Back Guarantee</h2>
<div class="highlight">
If you are not satisfied with the {BRAND} API service, you may request a full refund within <strong>14 days</strong> of your initial purchase or subscription renewal, no questions asked.
</div>

<h2>How to Request a Refund</h2>
<ol>
  <li>Email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> with your API key ID and the email associated with your account.</li>
  <li>Alternatively, use Paddle's buyer portal to request a refund directly.</li>
  <li>Refunds are processed within 5-10 business days through Paddle.</li>
</ol>

<h2>After 14 Days</h2>
<ul>
  <li>Refunds after the 14-day window are handled on a case-by-case basis.</li>
  <li>If the Service experienced significant downtime or errors during your billing period, we will issue a pro-rata credit or refund.</li>
  <li>Unused portions of a subscription are not refundable after the 14-day window.</li>
</ul>

<h2>Cancellation</h2>
<ul>
  <li>You may cancel your subscription at any time through Paddle's customer portal.</li>
  <li>Your API access remains active until the end of your current billing period.</li>
  <li>No further charges will be made after cancellation.</li>
  <li>The Free tier does not require cancellation — simply stop using the API.</li>
</ul>

<h2>Free Tier</h2>
<p>The Free tier is provided at no cost and is not subject to refunds.</p>

<h2>Contact</h2>
<p>For any billing questions: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</body></html>"""
