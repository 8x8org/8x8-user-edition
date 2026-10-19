package world.eightx8.user;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.widget.Button;
import android.widget.FrameLayout;
import android.view.Gravity;
import android.util.TypedValue;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import androidx.webkit.WebViewAssetLoader;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public final class MainActivity extends Activity {
  private static final int SELECT_MEDIA = 808;
  private static final String LOCAL_ORIGIN = "https://" + PublicAssetHandler.HOST;

  private static boolean permittedOrigin(Uri uri) {
    if (!"https".equals(uri.getScheme())) return false;
    if (uri.getPort() != -1 && uri.getPort() != 443) return false;
    String host = uri.getHost();
    String remote = Uri.parse(BuildConfig.HOME_URL).getHost();
    return host != null && (PublicAssetHandler.HOST.equalsIgnoreCase(host)
      || (remote != null && remote.equalsIgnoreCase(host)));
  }
  private WebView web;
  private ValueCallback<Uri[]> pendingSelection;

  @SuppressLint("SetJavaScriptEnabled")
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    web = new WebView(this);
    FrameLayout carrier = new FrameLayout(this);
    carrier.addView(web, new FrameLayout.LayoutParams(
      FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
    Button updates = new Button(this);
    updates.setText("8x8 Updates");
    updates.setTextSize(11);
    updates.setContentDescription("Check verified 8x8 Android updates");
    FrameLayout.LayoutParams updatePosition = new FrameLayout.LayoutParams(
      FrameLayout.LayoutParams.WRAP_CONTENT, FrameLayout.LayoutParams.WRAP_CONTENT);
    updatePosition.gravity = Gravity.TOP | Gravity.END;
    updatePosition.topMargin = (int) TypedValue.applyDimension(
      TypedValue.COMPLEX_UNIT_DIP, 6, getResources().getDisplayMetrics());
    updatePosition.rightMargin = (int) TypedValue.applyDimension(
      TypedValue.COMPLEX_UNIT_DIP, 8, getResources().getDisplayMetrics());
    updates.setOnClickListener(v -> VerifiedUpdateManager.check(this));
    carrier.addView(updates, updatePosition);
    setContentView(carrier);
    WebSettings s = web.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setAllowFileAccess(false);
    // The picker grants a single user-selected content URI, not filesystem access.
    s.setAllowContentAccess(true);
    s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    s.setMediaPlaybackRequiresUserGesture(true);
    final WebViewAssetLoader bundled = new WebViewAssetLoader.Builder()
      .setDomain(PublicAssetHandler.HOST)
      .addPathHandler("/", new PublicAssetHandler(this)).build();
    web.setWebViewClient(new WebViewClient() {
      @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
        return bundled.shouldInterceptRequest(request.getUrl());
      }
      @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
        if (!request.isForMainFrame()) return false;
        // Local public projection or previously approved remote site only.
        return !permittedOrigin(request.getUrl());
      }
    });
    web.setWebChromeClient(new WebChromeClient() {
      @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
        Uri page = Uri.parse(view.getUrl() == null ? "" : view.getUrl());
        String path = page.getPath();
        boolean trusted = permittedOrigin(page)
          && ("/studio".equals(path) || "/studio/".equals(path) || "/studio/index.html".equals(path));
        if (!trusted) { callback.onReceiveValue(null); return true; }
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
    // Serve real Studio and Agent Room without depending on the older remote fallback site.
    web.loadUrl(LOCAL_ORIGIN + "/index.html?carrier=android");
  }

  @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if (requestCode != SELECT_MEDIA || pendingSelection == null) return;
    ValueCallback<Uri[]> callback = pendingSelection;
    pendingSelection = null;
    Uri selected = resultCode == RESULT_OK && data != null ? data.getData() : null;
    // A picker can return an arbitrary URI. Accept only scoped content: media.
    String mime = selected != null && "content".equals(selected.getScheme())
      ? getContentResolver().getType(selected) : null;
    boolean permitted = mime != null && (mime.startsWith("image/") || mime.startsWith("video/") || mime.startsWith("audio/"));
    callback.onReceiveValue(permitted ? new Uri[]{selected} : null);
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
