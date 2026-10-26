package com.copetrolite.technician;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceError;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

public final class MainActivity extends Activity {
    private static final String LOCAL_HOST = "192.168.1.64";
    private static final int LOCAL_PORT = 5173;
    private WebView webView;
    private FrameLayout root;
    private LinearLayout loadingPanel;
    private LinearLayout errorPanel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.rgb(1, 51, 60));
        getWindow().setNavigationBarColor(Color.rgb(1, 51, 60));
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);

        root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(244, 248, 248));
        webView = new WebView(this);
        webView.setBackgroundColor(Color.WHITE);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setSupportZoom(false);
        webView.getSettings().setAllowFileAccess(false);
        webView.getSettings().setAllowContentAccess(false);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        webView.setVisibility(View.INVISIBLE);
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return handleNavigation(request.getUrl());
            }

            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                loadingPanel.setVisibility(View.VISIBLE);
                errorPanel.setVisibility(View.GONE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                loadingPanel.setVisibility(View.GONE);
                webView.setVisibility(View.VISIBLE);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    loadingPanel.setVisibility(View.GONE);
                    webView.setVisibility(View.INVISIBLE);
                    errorPanel.setVisibility(View.VISIBLE);
                }
            }
        });
        root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        loadingPanel = createStatusPanel(true);
        errorPanel = createStatusPanel(false);
        errorPanel.setVisibility(View.GONE);
        root.addView(loadingPanel, centeredPanelParams());
        root.addView(errorPanel, centeredPanelParams());
        setContentView(root);
        webView.loadUrl("http://" + LOCAL_HOST + ":" + LOCAL_PORT + "/tech/login");
    }

    private FrameLayout.LayoutParams centeredPanelParams() {
        return new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT, Gravity.CENTER);
    }

    private LinearLayout createStatusPanel(boolean loading) {
        LinearLayout panel = new LinearLayout(this);
        panel.setGravity(Gravity.CENTER);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(36, 40, 36, 40);

        ImageView appIcon = new ImageView(this);
        appIcon.setImageResource(com.copetrolite.technician.R.drawable.ic_launcher);
        LinearLayout.LayoutParams iconParams = new LinearLayout.LayoutParams(dp(72), dp(72));
        iconParams.bottomMargin = 20;
        panel.addView(appIcon, iconParams);

        TextView brand = new TextView(this);
        brand.setText("COPETROLITE");
        brand.setTextColor(Color.rgb(1, 51, 60));
        brand.setTextSize(22);
        brand.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        brand.setLetterSpacing(0.08f);
        panel.addView(brand);

        TextView subtitle = new TextView(this);
        subtitle.setText("ESPACE TECHNICIEN");
        subtitle.setTextColor(Color.rgb(0, 109, 101));
        subtitle.setTextSize(11);
        subtitle.setLetterSpacing(0.12f);
        LinearLayout.LayoutParams subtitleParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        subtitleParams.bottomMargin = 32;
        panel.addView(subtitle, subtitleParams);

        if (loading) {
            ProgressBar progress = new ProgressBar(this);
            progress.setIndeterminateTintList(android.content.res.ColorStateList.valueOf(Color.rgb(0, 109, 101)));
            panel.addView(progress);
            TextView status = new TextView(this);
            status.setText("Connexion à votre espace…");
            status.setTextColor(Color.rgb(97, 122, 128));
            status.setTextSize(14);
            LinearLayout.LayoutParams statusParams = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            statusParams.topMargin = 18;
            panel.addView(status, statusParams);
        } else {
            TextView title = new TextView(this);
            title.setText("Serveur inaccessible");
            title.setTextColor(Color.rgb(1, 51, 60));
            title.setTextSize(20);
            title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
            panel.addView(title);

            TextView explanation = new TextView(this);
            explanation.setText("Vérifiez que votre téléphone et l’ordinateur sont sur le même Wi-Fi, puis réessayez.");
            explanation.setTextColor(Color.rgb(97, 122, 128));
            explanation.setTextSize(14);
            explanation.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams explanationParams = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            explanationParams.topMargin = 12;
            explanationParams.bottomMargin = 22;
            panel.addView(explanation, explanationParams);

            Button retry = new Button(this);
            retry.setText("Réessayer");
            retry.setTextColor(Color.WHITE);
            retry.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(1, 51, 60)));
            retry.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    webView.reload();
                }
            });
            panel.addView(retry);
        }
        return panel;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private boolean handleNavigation(Uri uri) {
        String scheme = uri.getScheme();
        if ("http".equals(scheme)
                && LOCAL_HOST.equals(uri.getHost())
                && uri.getPort() == LOCAL_PORT) {
            return false;
        }
        if ("http".equals(scheme) || "https".equals(scheme)) {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
        }
        return true;
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else if (errorPanel != null && errorPanel.getVisibility() == View.VISIBLE) {
            webView.reload();
        } else {
            super.onBackPressed();
        }
    }
}
