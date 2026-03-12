Tipps und Tricks

- Android: HTTP-only Setting muss gesetzt sein: https://developer.android.com/guide/topics/manifest/application-element#usesCleartextTraffic

Applogs ausgeben

```bash
adb shell am start -a android.intent.action.VIEW \
	-d "enmeshed-dev://localhost/bootstrap?defaultProfileName=Peter+Langweilig&truncatedReference=" "eu.enmeshed.app.dev"

app_pid="$(adb shell pidof eu.enmeshed.app.dev)"
adb logcat --pid="$app_pid" | grep '\[bootstrap\]'
```

