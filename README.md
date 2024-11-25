> [!IMPORTANT]
> This repository has been archived. The `autohouse` functionality was moved into the [ueo-watch](https://github.com/theunitedeffort/ueo-watch) repository.

# autohouse
Tool to automatically search for housing on theunitedeffort.org.  Autohouse will search for properties matching a given set of search parameters.  These search parameters are stored on Google Drive in a Google Sheet.

## Setup
The below assumes the existence of a Google Cloud project.

### Create a Google Cloud service account
1. Go to Cloud Console [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts).
1. Create a new service account with no roles.
1. Clicking on the new service account on the [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) page and go to the Keys tab.
1. Add a new JSON key by selecting **Add key > Create new key** and choose the JSON option.
1. Save the key in a secure location.

### Enable Google Drive API
1. Go to the [Google Drive API](https://console.developers.google.com/apis/api/drive.googleapis.com/overview) on the APIs & Services page of your Google Cloud project.
1. Click on Enable API.

### Share search parameters spreadsheet with the service account
1. Find the spreadsheet containing housing search parameters on Google Drive.
1. Using the Drive UI, share the spreadsheet with the email address associated with the new service account.  It will likely be of the form `{ID}@{PROJECT}.iam.gserviceaccount.com`.  Provide **view-only** access to this email address.
