package world.eightx8.user;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.Locale;
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
  private TextToSpeech tts;
  private boolean ttsReady=false;
  private static final int VOICE_INTENT_REQUEST=7308;

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
    // Buttons are native explicit-action controls. No ambient microphone and
    // no fake agent model output. Device recognizer may have its own privacy
    // and cloud-processing terms; Android's system consent UI applies.
    Button speak=new Button(this);
    speak.setText("Speak");
    speak.setContentDescription("Speak a local 8x8 status using Android TTS");
    speak.setOnClickListener(v->speakStatus());
    header.addView(speak,new LinearLayout.LayoutParams(
      ViewGroup.LayoutParams.WRAP_CONTENT,ViewGroup.LayoutParams.WRAP_CONTENT));
    Button talk=new Button(this);
    talk.setText("Talk");
    talk.setContentDescription("Ask Android recognizer to listen once with owner consent");
    talk.setOnClickListener(v->requestOneShotSpeech());
    header.addView(talk,new LinearLayout.LayoutParams(
      ViewGroup.LayoutParams.WRAP_CONTENT,ViewGroup.LayoutParams.WRAP_CONTENT));
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
    tts=new TextToSpeech(getApplicationContext(), status->{
      if(status==TextToSpeech.SUCCESS && tts!=null){
        int lang=tts.setLanguage(Locale.US);
        ttsReady=lang!=TextToSpeech.LANG_MISSING_DATA &&
                 lang!=TextToSpeech.LANG_NOT_SUPPORTED;
      }else ttsReady=false;
    });
    web.loadUrl(BuildConfig.HOME_URL + "/?carrier=android");
  }

  private void speakStatus() {
    if(!ttsReady || tts==null){
      Toast.makeText(this,"Android speech engine is unavailable.",Toast.LENGTH_SHORT).show();
      return;
    }
    // Status is intentionally static until a tenant-bound signed event feed
    // connects. Never recite secrets, private file content or model thoughts.
    tts.speak("8x8 One Fabric native voice preview. The live owner agent "
       +"and ChatGPT bridge are not connected. Your app can speak this status "
       +"through Android text to speech after you tap Speak.",
       TextToSpeech.QUEUE_FLUSH,null,"8x8-owner-voice-preview");
  }

  private void requestOneShotSpeech() {
    try{
      Intent intent=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
      intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                     RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
      intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE,Locale.US.toLanguageTag());
      intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,1);
      intent.putExtra(RecognizerIntent.EXTRA_PROMPT,
                     "8x8 local commands: open, close, speak status, stop voice");
      startActivityForResult(intent,VOICE_INTENT_REQUEST);
    }catch(ActivityNotFoundException e){
      Toast.makeText(this,"No Android speech recognizer available.",Toast.LENGTH_SHORT).show();
    }catch(SecurityException e){
      Toast.makeText(this,"Speech permission was not granted.",Toast.LENGTH_SHORT).show();
    }
  }

  @Override protected void onActivityResult(int requestCode,int resultCode,Intent data) {
    super.onActivityResult(requestCode,resultCode,data);
    if(requestCode!=VOICE_INTENT_REQUEST || resultCode!=RESULT_OK || data==null)return;
    ArrayList<String> results=data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
    if(results==null || results.isEmpty() || results.get(0)==null)return;
    String command=results.get(0).toLowerCase(Locale.US).trim().replaceAll("[.!?]+$","");
    if(command.matches("(open|show|open observatory|show status|show observatory)")){
      showPanel();
    }else if(command.matches("(close|close bubble|hide observatory)")){
      hidePanel();
    }else if(command.matches("(speak status|read status|talk to me)")){
      speakStatus();
    }else if(command.matches("(stop voice|be quiet|stop speaking)")){
      if(tts!=null)tts.stop(); // Local audio only, not owner STOP.
    }else{
      Toast.makeText(this,"Unsupported local speech command; no action.",
                     Toast.LENGTH_SHORT).show();
    }
    // Never save, echo, log, network-send or hand recognizer transcripts
    // to unverified agent runtimes. Global device commands are not allowed.
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
    if(tts!=null)tts.stop();
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
    if(tts!=null){tts.stop();tts.shutdown();tts=null;}
    if(observatory!=null){observatory.stopLoading();observatory.destroy();observatory=null;}
    if(web!=null){web.stopLoading();web.destroy();web=null;}
    panel=null;surface=null;
    super.onDestroy();
  }
}
