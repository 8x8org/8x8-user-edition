package world.eightx8.user;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * ©8x8 World Android web-carrier.
 *
 * The 8x8 bubble is an IN-ACTIVITY overlay only. It never uses
 * SYSTEM_ALERT_WINDOW, AccessibilityService, ADB, MediaProjection or a
 * foreground service. It cannot appear over ChatGPT or any other app.
 *
 * Production-native owner telemetry, persistent agent runtimes and signed APK
 * release remain separately consented and evidence gated.
 */
public final class MainActivity extends Activity {
  private WebView web;
  private WebView observatory;
  private LinearLayout panel;
  private FrameLayout surface;
  private boolean observatoryOpened;

  private int dp(int value) {
    return Math.round(value * getResources().getDisplayMetrics().density);
  }

  private GradientDrawable background(int fill, int stroke, float radius) {
    GradientDrawable d = new GradientDrawable();
    d.setColor(fill);
    d.setCornerRadius(dp((int)radius));
    d.setStroke(dp(1), stroke);
    return d;
  }

  @SuppressLint("SetJavaScriptEnabled")
  private void configure(WebView target) {
    WebSettings s=target.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setAllowFileAccess(false);
    s.setAllowContentAccess(false);
    s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    s.setMediaPlaybackRequiresUserGesture(true);
    target.setWebViewClient(new WebViewClient());
    target.setWebChromeClient(new WebChromeClient());
  }

  @SuppressLint("SetJavaScriptEnabled")
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    surface=new FrameLayout(this);
    web=new WebView(this);
    configure(web);
    surface.addView(web,new FrameLayout.LayoutParams(
      ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT));

    panel=new LinearLayout(this);
    panel.setOrientation(LinearLayout.VERTICAL);
    panel.setBackground(background(Color.rgb(7,26,43),Color.rgb(99,166,197),18));
    panel.setElevation(dp(12));
    panel.setVisibility(View.GONE);
    FrameLayout.LayoutParams overlaySize=new FrameLayout.LayoutParams(
      ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT);
    overlaySize.setMargins(dp(12),dp(44),dp(12),dp(70));
    overlaySize.gravity=Gravity.CENTER;
    surface.addView(panel,overlaySize);

    LinearLayout header=new LinearLayout(this);
    header.setPadding(dp(12),dp(8),dp(12),dp(8));
    header.setGravity(Gravity.CENTER_VERTICAL);
    TextView label=new TextView(this);
    label.setText("⚡ 8x8 Observatory · Source preview");
    label.setTextColor(Color.WHITE);
    label.setTextSize(13);
    LinearLayout.LayoutParams titleSize=new LinearLayout.LayoutParams(
      0,ViewGroup.LayoutParams.WRAP_CONTENT,1f);
    header.addView(label,titleSize);
    Button close=new Button(this);
    close.setText("Close");
    close.setContentDescription("Close in-app 8x8 Observatory");
    close.setOnClickListener(v->hidePanel());
    header.addView(close,new LinearLayout.LayoutParams(
      ViewGroup.LayoutParams.WRAP_CONTENT,ViewGroup.LayoutParams.WRAP_CONTENT));
    panel.addView(header,new LinearLayout.LayoutParams(
      ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));

    observatory=new WebView(this);
    configure(observatory);
    panel.addView(observatory,new LinearLayout.LayoutParams(
      ViewGroup.LayoutParams.MATCH_PARENT,0,1f));

    TextView bubble=new TextView(this);
    bubble.setText("8×8");
    bubble.setTextColor(Color.WHITE);
    bubble.setTextSize(17);
    bubble.setGravity(Gravity.CENTER);
    bubble.setContentDescription("Open the 8x8 Observatory bubble in this app");
    bubble.setBackground(background(Color.rgb(15,86,120),Color.rgb(134,216,245),32));
    bubble.setElevation(dp(18));
    bubble.setOnClickListener(v->{
      if(panel.getVisibility()==View.VISIBLE)hidePanel();else showPanel();
    });
    FrameLayout.LayoutParams bubbleSize=new FrameLayout.LayoutParams(dp(60),dp(60),
      Gravity.END|Gravity.BOTTOM);
    bubbleSize.setMargins(0,0,dp(18),dp(18));
    surface.addView(bubble,bubbleSize);

    setContentView(surface);
    web.loadUrl(BuildConfig.HOME_URL + "/?carrier=android");
  }

  private void showPanel() {
    if(panel==null||observatory==null)return;
    panel.setVisibility(View.VISIBLE);
    if(!observatoryOpened) {
      observatoryOpened=true;
      observatory.loadUrl(BuildConfig.HOME_URL + "/observatory/?carrier=android");
    }
  }

  private void hidePanel() {
    if(panel!=null)panel.setVisibility(View.GONE);
  }

  @Override public void onBackPressed() {
    if(panel!=null&&panel.getVisibility()==View.VISIBLE){
      if(observatory!=null&&observatory.canGoBack())observatory.goBack();
      else hidePanel();
    }else if(web!=null&&web.canGoBack())web.goBack();
    else super.onBackPressed();
  }

  @Override protected void onPause() {
    hidePanel(); // Owner activity outside 8x8 preempts the visible overlay.
    if(observatory!=null)observatory.onPause();
    if(web!=null)web.onPause();
    super.onPause();
  }

  @Override protected void onResume() {
    super.onResume();
    if(web!=null)web.onResume();
    if(observatory!=null)observatory.onResume();
  }

  @Override protected void onDestroy() {
    if(observatory!=null){observatory.stopLoading();observatory.destroy();observatory=null;}
    if(web!=null){web.stopLoading();web.destroy();web=null;}
    panel=null;surface=null;
    super.onDestroy();
  }
}
