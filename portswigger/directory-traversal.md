## File path traversal, simple case

If you refresh the page and intercept the request, there's this request to get the image

![image1](/images/portswigger-file-path-traversal-simplecase/portswigger-file-path-traversal-simplecase1.png)

Now add `../../../../` to go the the `/` directory and at the end add `/etc/passwd` to see the file

![image2](/images/portswigger-file-path-traversal-simplecase/portswigger-file-path-traversal-simplecase2.png)
