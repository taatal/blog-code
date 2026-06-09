resource "aws_cloudwatch_metric_alarm" "api_5xx" {
  alarm_name          = "api-5xx-rate-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 5

  metric_query {
    id          = "error_rate"
    expression  = "(errors / requests) * 100"
    label       = "5xx Error Rate"
    return_data = true
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "HTTPCode_Target_5XX_Count"
      namespace   = "AWS/ApplicationELB"
      period      = 60
      stat        = "Sum"
      dimensions = {
        LoadBalancer = aws_lb.api.arn_suffix
      }
    }
  }

  metric_query {
    id = "requests"
    metric {
      metric_name = "RequestCount"
      namespace   = "AWS/ApplicationELB"
      period      = 60
      stat        = "Sum"
      dimensions = {
        LoadBalancer = aws_lb.api.arn_suffix
      }
    }
  }
}

resource "aws_cloudwatch_dashboard" "deploy" {
  dashboard_name = "api-deployment"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title   = "Response Time (p50, p95, p99)"
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.api.arn_suffix, { stat = "p50" }],
            ["...", { stat = "p95" }],
            ["...", { stat = "p99" }]
          ]
          period = 60
          annotations = {
            horizontal = [{ value = 0.5, label = "SLA threshold (500ms)" }]
          }
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title   = "Active Connections & Request Rate"
          metrics = [
            ["AWS/ApplicationELB", "ActiveConnectionCount", "LoadBalancer", aws_lb.api.arn_suffix],
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.api.arn_suffix]
          ]
          period = 60
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title   = "ECS CPU & Memory"
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", "api-cluster", "ServiceName", "api-service"],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", "api-cluster", "ServiceName", "api-service"]
          ]
          period = 60
        }
      }
    ]
  })
}
