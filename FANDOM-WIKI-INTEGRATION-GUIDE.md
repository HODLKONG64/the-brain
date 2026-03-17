# FANDOM WIKI INTEGRATION GUIDE

## 1. Fandom Wiki API URL Formats
The Fandom Wiki API provides various endpoints to interact with wiki content. The base URL format is:

```
https://<wiki_id>.fandom.com/api.php
```

### Example
To access the API for the GK Wiki:
```
https://gkniftyheads.fandom.com/api.php
```

## 2. OAuth Authentication Flow
To use the Fandom Wiki API, OAuth authentication is required. Here’s a brief overview of the flow:

1. **Request OAuth Token**: Obtain a request token from the Fandom OAuth service.
2. **User Authorization**: Redirect the user to the authorization URL where they can grant access.
3. **Retrieve Access Token**: Once authorized, retrieve the access token to make API requests on behalf of the user.

### Example Steps
- **Request Token Endpoint**: `https://<wiki_id>.fandom.com/api.php?action=query&meta=tokens&type=login&format=json`
- **Authorization URL**: `https://<wiki_id>.fandom.com/w/index.php?title=Special:OAuth&action=authorize&client_id=<client_id>&response_type=code`
- **Access Token Endpoint**: `https://<wiki_id>.fandom.com/api.php?action=query&meta=tokens&type=login&format=json`

## 3. Redirect Parameter Behavior
The `redirect=no` parameter is used in the authorization URL to bypass the automatic redirect after authorization:

### Usage
- Set `redirect=no` when constructing the authorization URL to prevent the user from being redirected immediately, allowing you to handle the response manually:
```
https://<wiki_id>.fandom.com/w/index.php?title=Special:OAuth&action=authorize&client_id=<client_id>&response_type=code&redirect=no
```

## 4. Linking to GK Wiki with Correct API Endpoints
When integrating with the GK Wiki, ensure that you use the following API endpoints as needed:
- **Get Page Content**: `https://gkniftyheads.fandom.com/api.php?action=parse&page=<page_title>&format=json`
- **Get All Pages**: `https://gkniftyheads.fandom.com/api.php?action=query&list=allpages&apnamespace=0&format=json`

### Example
To access the content of a specific page:
```
https://gkniftyheads.fandom.com/api.php?action=parse&page=Main_Page&format=json
```

## Conclusion
This guide provides essential details for integrating with the Fandom Wiki API. Always refer to the [Fandom API Documentation](https://www.mediawiki.org/wiki/API:Main_page) for the most up-to-date information.
