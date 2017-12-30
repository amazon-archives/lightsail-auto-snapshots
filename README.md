# Lightsail Auto Snapshots

An AWS Lambda function to automatically snapshot all Amazon Lightsail virtual
private servers in an account and retain them for a given number of days. The
included AWS Serverless Application Model (SAM) template will upload and create
the function, grant it the permissions necessary to list your Lightsail
instances and snapshots and create and delete snapshots, and schedule it to run
once per day.

## Usage

To install this function, ensure you have the [AWS Command Line Interface
(AWS CLI)][cli] installed and configured.

Run the deploy script and optionally specify the region to install the function
and the number of days for which snapshots should be retained. By default, the
script will install the function into your default configured region and retain
snapshots for 30 days.

```console
## Install in US East (Ohio) and retain snapshots for 15 days
REGION=us-east-2 DAYS=15 bin/deploy

## Install in the CLI's configured default region and retain snapshots for 90 days
DAYS=90 bin/deploy

## Install in EU (Ireland) and retain snapshots for 30 days
REGION=eu-west-1 bin/deploy

## Install in Asia Pacific (Tokyo) and create snapshot every day at 7:00pm UTC, retain snapshots for 30 days
REGION=ap-northeast-1 SCHEDULE="cron(0 19 * * ? *)" bin/deploy
```

## License

Copyright 2011-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

[http://aws.amazon.com/apache2.0/](http://aws.amazon.com/apache2.0/)

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

[cli]: https://aws.amazon.com/documentation/cli/
