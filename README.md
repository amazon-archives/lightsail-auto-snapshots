# Lightsail Auto Snapshots

An AWS Lambda function to automatically snapshot all Amazon Lightsail virtual
private servers in an account and retain them for a given number of days. The
included AWS Serverless Application Model (SAM) template will upload and create
the function, grant it the permissions necessary to list your Lightsail
instances and snapshots and create and delete snapshots, and schedule it to run
once per day.

## Usage

Run the deploy script and optionally specify the number of days for which
snapshots should be retained. If this parameter is omitted, the function will
keep snapshots for 14 days.

This will create all resources in US East (N. Virginia) as it is the only
Region that currently supports Amazon Lightsail.

```console
bin/deploy [RETENTION_DAYS]
```

## License

Copyright 2011-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

[http://aws.amazon.com/apache2.0/](http://aws.amazon.com/apache2.0/)

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
