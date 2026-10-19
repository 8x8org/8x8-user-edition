package world.eightx8.user;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public final class MainActivity extends Activity {
  private static final int SELECT_MEDIA = 808;
  private WebView web;
  private ValueCallback<Uri[]> pendingSelection;

  @SuppressLint("SetJavaScriptEnabled")
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    web = new WebView(this);
    setContentView(web);
    WebSettings s = web.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setAllowFileAccess(false);
    // The picker grants a single user-selected content URI, not filesystem access.
    s.setAllowContentAccess(true);
    s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    s.setMediaPlaybackRequiresUserGesture(true);
    web.setWebViewClient(new WebViewClient());
    web.setWebChromeClient(new WebChromeClient() {
      @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
        if (pendingSelection != null) pendingSelection.onReceiveValue(null);
        pendingSelection = callback;
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        intent.putExtra(Intent.EXTRA_MIME_TYPES, new String[]{"image/*", "video/*", "audio/*"});
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, false);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try {
          startActivityForResult(intent, SELECT_MEDIA);
        } catch (ActivityNotFoundException ex) {
          pendingSelection = null;
          callback.onReceiveValue(null);
        }
        return true;
      }
    });
    web.loadUrl(BuildConfig.HOME_URL + "/?carrier=android");
  }

  @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if (requestCode != SELECT_MEDIA || pendingSelection == null) return;
    ValueCallback<Uri[]> callback = pendingSelection;
    pendingSelection = null;
    callback.onReceiveValue(resultCode == RESULT_OK && data != null && data.getData() != null
      ? new Uri[]{data.getData()} : null);
  }

  @Override public void onBackPressed() {
    if (web != null && web.canGoBack()) web.goBack(); else super.onBackPressed();
  }

  @Override protected void onDestroy() {
    if (pendingSelection != null) { pendingSelection.onReceiveValue(null); pendingSelection = null; }
    if (web != null) { web.stopLoading(); web.destroy(); web = null; }
    super.onDestroy();
  }
}
