# FANDOM Wiki API Integration Rules

This document outlines the essential rules for integrating with the Fandom Wiki API, including authentication steps, rate limiting, URL formats, and error handling specifically for GK wiki updates.

## 1. Authentication Steps
To authenticate with the Fandom Wiki API:
- Obtain a valid API key from the Fandom developer portal.
- Include the API key in every request as a query parameter or in the request header.

Example:
```
GET https://www.fandom.com/api/v1/...
Headers:
Authorization: YOUR_API_KEY
```

## 2. Rate Limiting
- The Fandom Wiki API imposes rate limits to prevent abuse. Default limits are:
  - **100 requests per minute** for unauthenticated users.
  - **1000 requests per minute** for authenticated users.
- Exceeding these limits will result in a `429 Too Many Requests` error.
- Be sure to check for rate limiting headers in the response, such as `X-RateLimit-Limit` and `X-RateLimit-Remaining`.

## 3. URL Formats
- Base URL for API calls:
```
https://www.fandom.com/api/v1/
```
- Common endpoint examples:
  - Retrieve pages: `GET /article/`
  - Search: `GET /search/`

- Make sure to provide required parameters such as `namespace` and `title`.

## 4. Error Handling
When using the Fandom Wiki API, it's crucial to handle errors appropriately:
- **400 Bad Request**: Check your request parameters.
- **401 Unauthorized**: Ensure your API key is valid.
- **403 Forbidden**: Verify your permissions for the requested data.
- **404 Not Found**: The requested resource does not exist.
- **500 Internal Server Error**: The issue may be on the server side. Retry the request after some time.

## 5. GK Wiki Updates
When updating the GK wiki:
- Ensure that you follow the API rules above.
- Validate any changes against existing data structures and guidelines set by the wiki.