package world.eightx8.user;

import android.content.Context;
import android.content.res.AssetManager;
import android.webkit.WebResourceResponse;
import androidx.webkit.WebViewAssetLoader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/** Public-only static User Edition projection bundled inside the preview APK. */
public final class PublicAssetHandler implements WebViewAssetLoader.PathHandler {
  public static final String HOST = "appassets.androidplatform.net";
  private final AssetManager assets;

  public PublicAssetHandler(Context context) {
    this.assets = context.getAssets();
  }

  private static WebResourceResponse missing() {
    return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found",
        headers(false), new ByteArrayInputStream("Not Found".getBytes(StandardCharsets.UTF_8)));
  }

  private static Map<String,String> headers(boolean html) {
    Map<String,String> result = new HashMap<>();
    result.put("X-Content-Type-Options", "nosniff");
    result.put("Cache-Control", "no-store");
    result.put("Referrer-Policy", "no-referrer");
    if (html) {
      result.put("Content-Security-Policy",
          "default-src 'self'; script-src 'self' 'unsafe-inline' https://telegram.org; " +
          "style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; " +
          "media-src 'self' blob:; font-src 'self'; connect-src 'self' https://api.coingecko.com; " +
          "frame-src 'self'; manifest-src 'self'; worker-src 'self'; object-src 'none'; " +
          "base-uri 'self'; form-action 'none'");
    }
    return result;
  }

  private static String mime(String p) {
    if (p.endsWith(".html")) return "text/html";
    if (p.endsWith(".mjs") || p.endsWith(".js")) return "application/javascript";
    if (p.endsWith(".css")) return "text/css";
    if (p.endsWith(".svg")) return "image/svg+xml";
    if (p.endsWith(".webmanifest")) return "application/manifest+json";
    if (p.endsWith(".json")) return "application/json";
    if (p.endsWith(".png")) return "image/png";
    if (p.endsWith(".jpg") || p.endsWith(".jpeg")) return "image/jpeg";
    if (p.endsWith(".webp")) return "image/webp";
    if (p.endsWith(".gif")) return "image/gif";
    if (p.endsWith(".woff2")) return "font/woff2";
    return "application/octet-stream";
  }

  private static String route(String p) {
    switch (p) {
      case "": case "index.html": case "r3": case "first-blink": return "index.html";
      case "studio": case "studio/": return "studio/index.html";
      case "observatory": case "observatory/": return "observatory/index.html";
      case "agents": case "agents/": return "agents/index.html";
      case "atlas": case "atlas/": return "atlas/index.html";
      case "mcp/catalog": return "mcp/one-fabric-capability-catalog-v1.json";
      case "world": case "world/": case "stable": case "stable/":
      case "art-board": return "stable/index.html";
      case "telegram": case "telegram/": return "telegram/index.html";
      case "discord": case "discord/": return "discord/index.html";
      case "android": case "android/": return "android/index.html";
      case "presale": case "presale/": return "presale/index.html";
      case "projects": case "projects/": return "projects/index.html";
      default: return p;
    }
  }

  @Override public WebResourceResponse handle(String path) {
    String request = path == null ? "" : path;
    if (request.startsWith("/")) request = request.substring(1);
    // A contained read-only bundle is never an Android filesystem / private API gateway.
    if (request.contains("..") || request.contains("\\") || request.contains("%")
        || request.contains("?") || request.contains("#") || request.startsWith(".")
        || !request.matches("[A-Za-z0-9_./-]*")) return missing();
    String file = route(request);
    if (file.startsWith("api/") || file.startsWith("oauth/")
        || file.startsWith("private/") || file.startsWith("owner/")) return missing();
    try {
      InputStream bytes = assets.open(file, AssetManager.ACCESS_STREAMING);
      String kind = mime(file);
      return new WebResourceResponse(kind, "UTF-8", 200, "OK", headers("text/html".equals(kind)), bytes);
    } catch (IOException e) {
      return missing();
    }
  }
}
