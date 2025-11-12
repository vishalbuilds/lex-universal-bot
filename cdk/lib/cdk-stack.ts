import * as cdk from "aws-cdk-lib/core";
import { Construct } from "constructs";
import { aws_lex as lex } from "aws-cdk-lib";

// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class LexStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'CdkQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });
  }
}
