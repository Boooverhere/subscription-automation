from templates.email_templates import get_email_content

# Test all 4 stages
for stage in [1, 2, 3, 4]:
    content = get_email_content(
        stage=stage,
        customer_name="John",
        plan="6 Months Premium Subscription"
    )
    print(f"\n--- Stage {stage} ---")
    print(f"Subject: {content['subject']}")
    print(f"Body preview: {content['body'][:100].strip()}...")
