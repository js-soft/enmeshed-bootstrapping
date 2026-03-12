```json
// Connector
// createRelationshipTemplate
{
  "maxNumberOfAllocations": 100,
  "expiresAt": "2029-01-01T00:00:00.000Z",
  "content": {
    "@type": "RelationshipTemplateContent",
    "title": "Huhu =)",
    "onNewRelationship": {
      "@type": "Request",
      "items": [
        {
          "@type": "ConsentRequestItem",
          "consent": "...",
          "requiresInteraction": false,
          "mustBeAccepted": false
        }
      ]
    }
  }
}
```

Truncated ref auslesen: UkxUSjl2dmVYRjA4QWxvellWN1NAaHR0cDovL2NvbnN1bWVyLWFwaTo4MDgwfDN8d0lSaDRqaHlHc09mdFZqaWJJNGM3SjdlRE5faUtNazFSXzlvdWtROWluVXx8

```
Connector2: POST /api/core/v1/RelationshipTemplates/Peer

{
  "reference": "UkxUQ1FFN3lMcVkxZGszYWRUZm1AaHR0cDovL2NvbnN1bWVyLWFwaTo4MDgwfDN8RXFUenNXM1duQmxCb0tqV2dqdVNMUFVJa3hFbmQtN1QxZzd2aUFjMnFrUXx8"
}

```

```
Connector2:

{
  "templateId": "RLT_________________",
  "creationContent": {
   "@type": "RelationshipCreationContent",
    "response": {
      "items": [
        {
          "@type": "AcceptRequestItem",
          "accept": "true"
        }
      ]
    }
  }
}

# diesegut
{
      "requestId": "REQJwaDDUUh0XI7VRHPu",
      "result": "Accepted",
      "items": [
        {
          "@type": "AcceptResponseItem",
          "result": "Accepted"
        }
      ]
    }
```
