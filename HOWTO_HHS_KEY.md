# How to Get an HHS Key

This guide explains how to register for and obtain an API key (developer credential) from the
[US Department of Health & Human Services (HHS)](https://www.hhs.gov/) in order to access
HHS data services and APIs.

## What Is an HHS Key?

An HHS key is an API key (also called a developer credential or access token) issued by HHS or
one of its agencies (e.g. CMS, FDA, CDC). It authenticates your application when making
programmatic requests to HHS data APIs such as:

- [HealthData.gov](https://healthdata.gov/) datasets
- [data.cms.gov](https://data.cms.gov/) (Centers for Medicare & Medicaid Services)
- [openFDA](https://open.fda.gov/) (Food & Drug Administration)
- [CDC Open Data](https://data.cdc.gov/)

## Prerequisites

- A valid email address
- A brief description of your intended use of the data

## Step-by-Step: Register for an HHS / HealthData.gov API Key

1. **Go to the registration page**
   Navigate to <https://healthdata.gov/developers>.

2. **Click "Request an API Key"** (or the equivalent sign-up button on the page).

3. **Fill in the registration form**
   - First name and last name
   - Email address (used to deliver your key)
   - Organization / company name (optional)
   - Brief description of your use case

4. **Submit the form**
   Click **Submit** or **Sign Up**. You will receive a confirmation email shortly.

5. **Check your email**
   Open the email from HHS / HealthData.gov. It will contain:
   - Your **API key** (a long alphanumeric string)
   - Instructions for including the key in API requests

6. **Store your key safely**
   - Do **not** hard-code your key in source code or commit it to a public repository.
   - Store it in an environment variable or a secrets manager (e.g. GitHub Secrets,
     AWS Secrets Manager, HashiCorp Vault).

## Step-by-Step: Register for an openFDA API Key

1. Go to <https://open.fda.gov/apis/authentication/>.
2. Click **Get your API key**.
3. Enter your email address and click **Get API Key**.
4. Check your email for the key.

## Using Your Key in API Requests

Include your key as a query parameter named `api_key`:

```
https://api.healthdata.gov/some-endpoint?api_key=YOUR_KEY_HERE
```

Or as an HTTP header (where supported):

```
Authorization: Bearer YOUR_KEY_HERE
```

Refer to the specific API's documentation for the correct authentication method.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No email received | Check your spam folder; wait up to 15 minutes |
| Key is rejected (401) | Confirm you are sending it in the correct parameter or header |
| Rate-limit errors (429) | Reduce request frequency; consider requesting an elevated quota |
| Key is lost/forgotten | Re-register with the same email; a new key will be issued |

## Getting Help

- HHS Help Desk: <https://www.hhs.gov/contact/index.html>
- HealthData.gov support: <https://healthdata.gov/contact-us>
- openFDA FAQ: <https://open.fda.gov/about/faq/>

If you encounter an issue specific to this repository, open an
[issue](https://github.com/martin125470/Crewbot1501/issues) and describe the problem.
