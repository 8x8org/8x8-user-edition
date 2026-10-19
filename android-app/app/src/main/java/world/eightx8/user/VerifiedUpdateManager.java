package world.eightx8.user;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.cert.CertificateEncodingException;
import android.content.pm.Signature;
import org.json.JSONObject;

/**
 * User-initiated update path: fail closed, verify APK bytes + package + signer,
 * then hand over to Android's interactive package installer. Never silent install.
 * The first preview is separately identified; later updates require a stable
 * matching signing key. A missing release manifest never grants authority.
 */
public final class VerifiedUpdateManager {
  private static final int META_LIMIT = 8192;
  private static final long APK_LIMIT = 64L * 1024L * 1024L;
  private static final String SCHEMA = "eightx8.android.update.v1";
  private VerifiedUpdateManager() {}

  public static void check(Activity activity) {
    new AlertDialog.Builder(activity)
      .setTitle("8x8 Verified Updates")
      .setMessage("Check the official 8x8 update manifest? The app verifies package identity, version, checksum and signing certificate. Android must approve installation.")
      .setNegativeButton("Cancel", null)
      .setPositiveButton("Check", (d, w) -> {
        Toast.makeText(activity, "Checking verified 8x8 release…", Toast.LENGTH_SHORT).show();
        new Thread(() -> {
          try {
            UpdateCandidate next = downloadAndVerify(activity);
            activity.runOnUiThread(() -> offerInstall(activity, next));
          } catch (Exception ex) {
            // Do not show secrets or raw network URLs in UI or logs.
            activity.runOnUiThread(() -> new AlertDialog.Builder(activity)
              .setTitle("8x8 update not available")
              .setMessage("No compatible verified release can be installed: " + publicReason(ex))
              .setPositiveButton("OK", null).show());
          }
        }, "eightx8-verified-update").start();
      }).show();
  }

  private static String publicReason(Exception ex) {
    if (ex instanceof NotReleasedException) return "No promoted Android release is published for this app yet.";
    if (ex instanceof java.io.FileNotFoundException) return "The official update manifest is not deployed.";
    return "The release did not pass all verification checks or could not be retrieved.";
  }

  private static String origin() throws Exception {
    URL u = new URL(BuildConfig.HOME_URL);
    if (!"https".equals(u.getProtocol()) || u.getPort() != -1 || u.getHost().isEmpty()
       || !u.getPath().isEmpty() && !"/".equals(u.getPath()))
      throw new SecurityException("Invalid trusted origin");
    return "https://" + u.getHost();
  }

  private static HttpURLConnection connect(URL url, String expectedHost) throws Exception {
    if (!"https".equals(url.getProtocol()) || !expectedHost.equalsIgnoreCase(url.getHost())
      || url.getPort() != -1 || url.getUserInfo() != null || url.getRef() != null)
      throw new SecurityException("Untrusted update URL");
    HttpURLConnection c = (HttpURLConnection) url.openConnection();
    c.setInstanceFollowRedirects(false);
    c.setConnectTimeout(6000);
    c.setReadTimeout(15000);
    c.setRequestProperty("Accept", "application/json, application/octet-stream");
    if (c.getResponseCode() != 200) {
      c.disconnect();
      throw new java.io.FileNotFoundException("No verified update response");
    }
    return c;
  }

  private static byte[] readBounded(InputStream stream, int limit) throws Exception {
    java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
    byte[] buf = new byte[4096];
    int n;
    while ((n = stream.read(buf)) != -1) {
      if (out.size() + n > limit) throw new SecurityException("Metadata too large");
      out.write(buf, 0, n);
    }
    return out.toByteArray();
  }

  private static String hex(byte[] b) {
    final char[] digits = "0123456789abcdef".toCharArray();
    char[] out = new char[b.length*2];
    for(int i=0; i<b.length; i++) {
      int v = b[i]&255;
      out[i*2] = digits[v>>>4];
      out[i*2+1] = digits[v&15];
    }
    return new String(out);
  }

  private static String certDigest(Signature signature) throws Exception {
    return hex(MessageDigest.getInstance("SHA-256").digest(signature.toByteArray()));
  }

  private static String signer(PackageInfo info) throws Exception {
    if (info == null) throw new SecurityException("No package identity");
    if (Build.VERSION.SDK_INT >= 28) {
      if (info.signingInfo == null || info.signingInfo.getApkContentsSigners().length != 1)
        throw new SecurityException("Invalid signer set");
      return certDigest(info.signingInfo.getApkContentsSigners()[0]);
    }
    // Android 8.0 and 8.1: older public package-signature API.
    if (info.signatures == null || info.signatures.length != 1)
      throw new SecurityException("Invalid signer set");
    return certDigest(info.signatures[0]);
  }

  private static UpdateCandidate downloadAndVerify(Activity a) throws Exception {
    String host = new URL(origin()).getHost();
    URL manifest = new URL(origin() + "/updates/android/latest.json");
    JSONObject m;
    HttpURLConnection c = connect(manifest, host);
    try (InputStream in = c.getInputStream()) {
      m = new JSONObject(new String(readBounded(in, META_LIMIT), StandardCharsets.UTF_8));
    } finally { c.disconnect(); }
    if (!SCHEMA.equals(m.optString("schema"))) throw new SecurityException("Invalid schema");
    if (!m.optBoolean("available",false)) throw new NotReleasedException();
    String packageId = m.getString("packageId");
    if (!a.getPackageName().equals(packageId)) throw new SecurityException("Wrong package");
    long version = m.getLong("versionCode");
    PackageManager pm = a.getPackageManager();
    int signatureFlag = Build.VERSION.SDK_INT >= 28
      ? PackageManager.GET_SIGNING_CERTIFICATES : PackageManager.GET_SIGNATURES;
    PackageInfo installed = pm.getPackageInfo(a.getPackageName(), signatureFlag);
    if (version <= installed.getLongVersionCode()) throw new NotReleasedException();
    String sha = m.getString("sha256");
    String cert = m.getString("signerSha256");
    if (!sha.matches("[a-f0-9]{64}") || !cert.matches("[a-f0-9]{64}"))
      throw new SecurityException("Invalid digest");
    if (!cert.equals(signer(installed))) throw new SecurityException("Signing identity mismatch");
    URL apk = new URL(m.getString("apkUrl"));
    String path = apk.getPath();
    if (!path.matches("/updates/android/[A-Za-z0-9_.-]+\\.apk") || path.contains("..")
      || apk.getQuery() != null || !host.equalsIgnoreCase(apk.getHost()))
      throw new SecurityException("Invalid package path");
    File tmp = new File(a.getCacheDir(), "verified-update.part");
    File verified = new File(a.getCacheDir(), "verified-update.apk");
    if (tmp.exists() && !tmp.delete()) throw new SecurityException("Cannot reset staging");
    HttpURLConnection dl = connect(apk, host);
    try {
      long length = dl.getContentLengthLong();
      if (length > APK_LIMIT) throw new SecurityException("Package too large");
      MessageDigest md = MessageDigest.getInstance("SHA-256");
      long total=0;
      try (InputStream in=dl.getInputStream(); FileOutputStream out=new FileOutputStream(tmp)) {
        byte[] buffer=new byte[32768]; int n;
        while((n=in.read(buffer))!=-1) {
          total+=n;
          if (total>APK_LIMIT) throw new SecurityException("Package too large");
          md.update(buffer,0,n); out.write(buffer,0,n);
        }
        out.getFD().sync();
      }
      if (total==0 || !sha.equals(hex(md.digest()))) throw new SecurityException("Checksum mismatch");
      PackageInfo archive = pm.getPackageArchiveInfo(tmp.getAbsolutePath(),signatureFlag);
      if (archive==null || !packageId.equals(archive.packageName)
        || archive.getLongVersionCode()!=version || !cert.equals(signer(archive)))
        throw new SecurityException("APK identity mismatch");
      if (verified.exists() && !verified.delete()) throw new SecurityException("Cannot replace staging");
      if (!tmp.renameTo(verified)) throw new SecurityException("Cannot finalize staging");
    } finally { dl.disconnect(); if(tmp.exists()) tmp.delete(); }
    return new UpdateCandidate(verified, m.optString("notes","A verified update is ready."));
  }

  private static void offerInstall(Activity a, UpdateCandidate next) {
    new AlertDialog.Builder(a).setTitle("Verified update ready")
      .setMessage(next.notes + "\nAndroid will ask you to approve the installation. Your existing app data is not removed.")
      .setNegativeButton("Later", null)
      .setPositiveButton("Install", (d,w)-> {
        if (Build.VERSION.SDK_INT >= 26 && !a.getPackageManager().canRequestPackageInstalls()) {
          try {
            Intent settings = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
              Uri.parse("package:"+a.getPackageName()));
            a.startActivity(settings);
            Toast.makeText(a,"Allow this app to request installs, then tap Update again.",Toast.LENGTH_LONG).show();
          } catch (ActivityNotFoundException ex) {
            Toast.makeText(a,"Android installer authorization is unavailable.",Toast.LENGTH_LONG).show();
          }
          return;
        }
        Uri uri = Uri.parse("content://" + a.getPackageName() + ".updater/verified-update.apk");
        Intent install=new Intent(Intent.ACTION_VIEW);
        install.setDataAndType(uri,"application/vnd.android.package-archive");
        install.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try { a.startActivity(install); }
        catch (ActivityNotFoundException ex) {
          Toast.makeText(a,"No Android installer is available.",Toast.LENGTH_LONG).show();
        }
      }).show();
  }

  private static final class UpdateCandidate {
    final File file; final String notes;
    UpdateCandidate(File file,String notes) {this.file=file;this.notes=notes;}
  }
  private static final class NotReleasedException extends Exception {}
}