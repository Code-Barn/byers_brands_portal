"""
Django template tags for Polly polls and Cactus Comments integration.
"""
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag('polly_client/poll_widget.html')
def render_poll(poll, theme='light'):
    """
    Render a poll as a widget.

    Usage:
        {% render_poll poll 'light' %}
    """
    return {
        'poll': poll,
        'theme': theme,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    }


@register.inclusion_tag('polly_client/poll_list.html')
def render_poll_list(polls, theme='light'):
    """
    Render a list of polls.

    Usage:
        {% render_poll_list polls 'dark' %}
    """
    return {
        'polls': polls,
        'theme': theme,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    }


@register.simple_tag
def cactus_comments(poll_id, site_name=None):
    """
    Render Cactus Comments section for a poll.

    Usage:
        {% cactus_comments poll.id %}
        {% cactus_comments poll.id "my-site" %}
    """
    if site_name is None:
        site_name = getattr(settings, 'CACTUS_SITE_NAME', 'byers-brands-llc')

    homeserver_url = getattr(settings, 'CACTUS_HOMESERVER_URL', 'https://matrix.cactus.chat:8448')
    server_name = getattr(settings, 'CACTUS_SERVER_NAME', 'cactus.chat')
    comment_section_id = f"poll_{poll_id}"

    return mark_safe(f'''
    <div class="cactus-comments-wrapper"
         data-site-name="{site_name}"
         data-comment-section-id="{comment_section_id}"
         data-homeserver-url="{homeserver_url}"
         data-server-name="{server_name}">
        <div id="cactus-comments-{poll_id}" class="cactus-comments-container">
            <p class="cactus-loading text-gray-500 dark:text-gray-400">Loading comments...</p>
        </div>
    </div>
    <script>
    (function() {{
        function loadCactusComments() {{
            if (typeof initComments !== 'undefined') {{
                initComments({{
                    node: document.getElementById('cactus-comments-{poll_id}'),
                    defaultHomeserverUrl: '{homeserver_url}',
                    serverName: '{server_name}',
                    siteName: '{site_name}',
                    commentSectionId: '{comment_section_id}',
                    pageSize: 10,
                    loginEnabled: true,
                    guestPostingEnabled: true
                }});
            }} else {{
                var script = document.createElement('script');
                script.src = 'https://cactus.chat/cactus.js';
                script.onload = function() {{
                    initComments({{
                        node: document.getElementById('cactus-comments-{poll_id}'),
                        defaultHomeserverUrl: '{homeserver_url}',
                        serverName: '{server_name}',
                        siteName: '{site_name}',
                        commentSectionId: '{comment_section_id}',
                        pageSize: 10,
                        loginEnabled: true,
                        guestPostingEnabled: true
                    }});
                }};
                document.head.appendChild(script);

                var link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = 'https://cactus.chat/style.css';
                document.head.appendChild(link);
            }}
        }}

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', loadCactusComments);
        }} else {{
            loadCactusComments();
        }}
    }})();
    </script>
    ''')


@register.simple_tag
def polly_config():
    """Get Polly configuration for JavaScript."""
    return mark_safe(json.dumps({
        'apiUrl': '/polly/api/',
        'embeddingApp': getattr(settings, 'POLLY_EMBEDDING_APP', 'byers-brands-llc'),
        'siteName': getattr(settings, 'CACTUS_SITE_NAME', 'byers-brands-llc'),
    }))


import json