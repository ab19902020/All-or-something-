package com.unitedroad.studio

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private val fileRequestCode = 4701

    @SuppressLint("SetJavaScriptEnabled")
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
}
