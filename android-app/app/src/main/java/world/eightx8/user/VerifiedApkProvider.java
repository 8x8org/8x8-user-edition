package world.eightx8.user;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;
import java.io.File;
import java.io.FileNotFoundException;

/** Read-only one-file capability for Android's interactive package installer. */
public final class VerifiedApkProvider extends ContentProvider {
  private static final String FILE = "verified-update.apk";
  private File verified(Uri uri) throws FileNotFoundException {
    if (getContext()==null || uri==null
      || !("content".equals(uri.getScheme()))
      || !uri.getAuthority().equals(getContext().getPackageName()+".updater")
      || !("/"+FILE).equals(uri.getPath())
      || uri.getQuery()!=null || uri.getFragment()!=null)
      throw new FileNotFoundException("Not an authorized update");
    File file = new File(getContext().getCacheDir(),FILE);
    if (!file.isFile()) throw new FileNotFoundException("No verified update");
    return file;
  }
  @Override public boolean onCreate() { return true; }
  @Override public String getType(Uri uri) { return "application/vnd.android.package-archive"; }
  @Override public Cursor query(Uri uri,String[] projection,String selection,String[] selectionArgs,String sortOrder) {
    try {
      File file=verified(uri);
      String[] cols=projection==null ? new String[]{OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE}:projection;
      MatrixCursor c=new MatrixCursor(cols,1);
      Object[] values=new Object[cols.length];
      for(int i=0;i<cols.length;i++) {
        if(OpenableColumns.DISPLAY_NAME.equals(cols[i])) values[i]=FILE;
        else if(OpenableColumns.SIZE.equals(cols[i])) values[i]=file.length();
      }
      c.addRow(values);
      return c;
    } catch(FileNotFoundException e) {return null;}
  }
  @Override public ParcelFileDescriptor openFile(Uri uri,String mode) throws FileNotFoundException {
    if (!"r".equals(mode)) throw new FileNotFoundException("Read only");
    return ParcelFileDescriptor.open(verified(uri),ParcelFileDescriptor.MODE_READ_ONLY);
  }
  @Override public Uri insert(Uri uri,ContentValues values) {throw new UnsupportedOperationException();}
  @Override public int delete(Uri uri,String selection,String[] selectionArgs) {throw new UnsupportedOperationException();}
  @Override public int update(Uri uri,ContentValues values,String selection,String[] selectionArgs) {throw new UnsupportedOperationException();}
}