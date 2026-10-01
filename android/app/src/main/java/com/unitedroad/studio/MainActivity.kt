package com.unitedroad.studio

import android.annotation.SuppressLint
import android.app.Activity
import android.content.ContentValues
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.util.Base64
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStream

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private val fileRequestCode = 4701

    private var exportStream: OutputStream? = null
    private var exportUri: Uri? = null
    private var exportFile: File? = null

    @SuppressLint("SetJavaScriptEnabled", "AddJavascriptInterface")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.databaseEnabled = true
        webView.settings.mediaPlaybackRequiresUserGesture = false
        webView.settings.allowContentAccess = true
        webView.settings.allowFileAccess = true
        webView.settings.loadWithOverviewMode = true
        webView.settings.useWideViewPort = true

        webView.addJavascriptInterface(AndroidBridge(), "UnitedRoadAndroid")
        webView.webViewClient = object : WebViewClient() {}

        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                callback: ValueCallback<Array<Uri>>?,
                params: FileChooserParams?
            ): Boolean {
                fileCallback?.onReceiveValue(null)
                fileCallback = callback

                val accepted = params?.acceptTypes
                    ?.filter { it.isNotBlank() }
                    ?.toTypedArray()
                    ?: emptyArray()

                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = if (accepted.size == 1) accepted[0] else "*/*"
                    putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true)
                    if (accepted.size > 1) putExtra(Intent.EXTRA_MIME_TYPES, accepted)
                }
                startActivityForResult(intent, fileRequestCode)
                return true
            }
        }

        webView.loadUrl("file:///android_asset/index.html")
    }

    inner class AndroidBridge {
        @JavascriptInterface
        fun beginExport(fileName: String, mimeType: String): Boolean {
            return try {
                closeExport()
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    val values = ContentValues().apply {
                        put(MediaStore.Downloads.DISPLAY_NAME, fileName)
                        put(MediaStore.Downloads.MIME_TYPE, mimeType)
                        put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/UnitedRoadStudio")
                        put(MediaStore.Downloads.IS_PENDING, 1)
                    }
                    exportUri = contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                    exportStream = exportUri?.let { contentResolver.openOutputStream(it, "w") }
                } else {
                    val dir = File(getExternalFilesDir(Environment.DIRECTORY_MOVIES), "UnitedRoadStudio")
                    dir.mkdirs()
                    exportFile = File(dir, fileName)
                    exportStream = FileOutputStream(exportFile!!)
                }
                exportStream != null
            } catch (_: Exception) {
                false
            }
        }

        @JavascriptInterface
        fun appendExport(base64Chunk: String): Boolean {
            return try {
                val bytes = Base64.decode(base64Chunk, Base64.DEFAULT)
                exportStream?.write(bytes)
                true
            } catch (_: Exception) {
                false
            }
        }

        @JavascriptInterface
        fun finishExport(): String {
            return try {
                exportStream?.flush()
                exportStream?.close()
                exportStream = null
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    exportUri?.let { uri ->
                        val values = ContentValues().apply { put(MediaStore.Downloads.IS_PENDING, 0) }
                        contentResolver.update(uri, values, null, null)
                    }
                }
                val result = exportUri?.toString() ?: exportFile?.absolutePath.orEmpty()
                runOnUiThread {
                    Toast.makeText(
                        this@MainActivity,
                        "Saved to Downloads/UnitedRoadStudio",
                        Toast.LENGTH_LONG
                    ).show()
                }
                result
            } catch (_: Exception) {
                ""
            } finally {
                exportUri = null
                exportFile = null
            }
        }

        @JavascriptInterface
        fun appVersion(): String = "0.3.0"
    }

    private fun closeExport() {
        try { exportStream?.close() } catch (_: Exception) {}
        exportStream = null
        exportUri = null
        exportFile = null
    }

    @Deprecated("Retained for Android WebView file picker compatibility")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == fileRequestCode) {
            val uris = mutableListOf<Uri>()
            if (resultCode == RESULT_OK && data != null) {
                data.clipData?.let { clip ->
                    for (i in 0 until clip.itemCount) uris.add(clip.getItemAt(i).uri)
                }
                data.data?.let { uris.add(it) }
            }
            fileCallback?.onReceiveValue(uris.toTypedArray())
            fileCallback = null
            return
        }
        super.onActivityResult(requestCode, resultCode, data)
    }

    @Deprecated("Handled for embedded browser navigation")
    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        closeExport()
        webView.destroy()
        super.onDestroy()
    }
}
