## send email api

url: POST https://api.resend.com/emails

```shell
curl -X POST 'https://api.resend.com/emails' \
     -H 'Authorization: Bearer re_123456789' \
     -H 'Content-Type: application/json' \
     -d $'{
  "from": "Acme <onboarding@resend.dev>",
  "to": ["delivered@resend.dev"],
  "subject": "hello world",
  "text": "it works!",
  "headers": {
    "X-Entity-Ref-ID": "123"
  },
  "attachments": [
    {
      "filename": 'invoice.pdf',
      "content": invoiceBuffer,
    },
  ]
}'
```

| params              | type             | required |
|---------------------|------------------|----------|
| from                | str              | True     |
| to                  | str or str[]     | True     |
| subject             | str              | True     |
| bcc                 | str or str[]     | False    | 
| cc                  | str or str[]     | False    | 
| reply_to            | str or str[]     | False    | 
| html                | str              | False    | 
| text                | str              | False    | 
| react               | str              | False    | 
| headers             | dict             | False    | 
| attachments         | list[attachment] | False    | 
| attachment.content  | buffer or str    | False    | 
| attachment.filename | str              | False    | 
| attachment.path     | str              | False    | 
| tags                | list[tag]        | False    | 
| tag.name            | str              | True     |
| value               | str              | False    | 

