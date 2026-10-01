package com.unitedroad.studio

import android.annotation.SuppressLint
import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.EditText
import android.widget.Toast

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private val fileRequestCode = 4701
    private val prefs by lazy { getSharedPreferences("urs_mobile", MODE_PRIVATE) }

    @SuppressLint("SetJavaScriptEnabled", "AddJavascriptInterface")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.mediaPlaybackRequiresUserGesture = false
        webView.settings.allowContentAccess = true
        webView.settings.allowFileAccess = true
        webView.settings.loadWithOverviewMode = true
        webView.settings.useWideViewPort = true

        webView.addJavascriptInterface(AndroidBridge(), "UnitedRoadAndroid")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                return false
            }

            override fun onPageFinished(view: WebView, url: String) {
                super.onPageFinished(view, url)
                title = "United Road Studio"
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                callback: ValueCallback<Array<Uri>>?,
                params: FileChooserParams?
            ): Boolean {
                fileCallback?.onReceiveValue(null)
                fileCallback = callback

                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                    putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true)
                    val accepted = params?.acceptTypes?.filter { it.isNotBlank() }?.toTypedArray()
                    if (!accepted.isNullOrEmpty()) putExtra(Intent.EXTRA_MIME_TYPES, accepted)
                }
                startActivityForResult(intent, fileRequestCode)
                return true
            }
        }

        val engine = prefs.getString("engine_url", "") ?: ""
        if (engine.isBlank()) showEngineDialog() else loadEngine(engine)
    }

    private fun normalizeEngine(value: String): String {
        var v = value.trim().trimEnd('/')
        if (!v.startsWith("http://") && !v.startsWith("https://")) v = "http://$v"
        return v
    }

    private fun loadEngine(value: String) {
        val engine = normalizeEngine(value)
        prefs.edit().putString("engine_url", engine).apply()
        webView.loadUrl("$engine/?android=1")
    }

    private fun showEngineDialog() {
        val input = EditText(this).apply {
            hint = "http://192.168.1.50:8765"
            setText(prefs.getString("engine_url", ""))
            selectAll()
        }
        AlertDialog.Builder(this)
            .setTitle("Connect to Studio Engine")
            .setMessage("Enter the address shown by United Road Studio on the engine computer. Keep the phone and computer on the same Wi-Fi.")
            .setView(input)
            .setCancelable(false)
            .setPositiveButton("Connect") { _, _ ->
                val value = input.text.toString()
                if (value.isBlank()) {
                    Toast.makeText(this, "Enter an engine address.", Toast.LENGTH_LONG).show()
                    showEngineDialog()
                } else {
                    loadEngine(value)
                }
            }
            .setNegativeButton("Close") { _, _ -> finish() }
            .show()
    }

    inner class AndroidBridge {
        @JavascriptInterface
        fun changeEngine() {
            runOnUiThread { showEngineDialog() }
        }
    }

    @Deprecated("Deprecated in Android API but retained for broad WebView compatibility")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == fileRequestCode) {
            val result = mutableListOf<Uri>()
            if (resultCode == RESULT_OK && data != null) {
                data.clipData?.let { clip ->
                    for (i in 0 until clip.itemCount) result.add(clip.getItemAt(i).uri)
                }
                data.data?.let { result.add(it) }
            }
            fileCallback?.onReceiveValue(result.toTypedArray())
            fileCallback = null
            return
        }
        super.onActivityResult(requestCode, resultCode, data)
    }

    @Deprecated("Handled for embedded browser navigation")
    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }
}
