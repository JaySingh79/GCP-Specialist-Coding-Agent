UPDATE AT 2026-10-31 15:37:59

- - Task: Create BigQuery dataset analytics_stage in project demo-dst with US location, description, and owner/environment labels.
1. Check active gcloud project/configuration and authenticate.
2. Inspect if the dataset analytics_stage already exists in project demo-dst.
3. Construct the gcloud/bq command for creating the dataset with location=US, description, and labels.
4. Execute the command with explicit --project flag.
5. Verify the created dataset configuration (location, description, labels).
UPDATE AT 2026-10-31 15:38:12

- # Todo Plan: Create BigQuery Dataset analytics_stage
1. Check active gcloud configuration and current project.
2. Verify if the target project demo-dst is accessible and if BigQuery API is enabled.
3. Discover the exact `gcloud bq datasets create` or `bq mk` command and its options using help.
4. Create the `analytics_stage` BigQuery dataset in project `demo-dst`, location `US`, with description and labels (owner, environment).
5. Verify that the dataset was successfully created with the correct properties.

