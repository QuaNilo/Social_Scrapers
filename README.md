# Social Scrapers

**Available Networks**  
``` ['twitter', 'instagram', 'reddit', 'tiktok', 'youtube', 'twitch', 'facebook'] ```

---

### Endpoints

**'/checkall_handle'**  

**Methods ['GET']**

**Parameters**  
- handle
    - String to hold the value of the handle we are looking for if it's available

**Parameter Restrictions**  
```None```

**Example**  
```localhost:5000/checkall_handle?handle=Cristiano```

**Output**

```
{
    "data": {
        "facebook": {
            "is_available": "Failure",
            "success": false
        },
        "instagram": {
            "is_available": false,
            "success": true
        },
        "reddit": {
            "is_available": false,
            "success": true
        },
        "tiktok": {
            "is_available": false,
            "success": true
        },
        "twitch": {
            "is_available": false,
            "success": true
        },
        "twitter": {
            "is_available": false,
            "success": true
        },
        "youtube": {
            "is_available": false,
            "success": true
        }
    },
    "success": true
}
```
2. **'/check_handle'** 

**Methods ['GET']**

**Parameters**  
- handle  
    - String to hold the value of the handle we are looking for if it's available  
- social_network
    - String to hold the value of the network you want to search for an available handle  
  

**Parameter Restrictions**  
```None```  

**Example**  
```localhost:5000/checkall_handle?handle=Cristiano```

**Output**
```
{
    "data": {
        "response": {
            "data": {
                "accept_followers": true,
                "awardee_karma": 0,
                "awarder_karma": 0,
                "comment_karma": 0,
                "created": 1151849710.0,
                "created_utc": 1151849710.0,
                "has_subscribed": false,
                "has_verified_email": false,
                "hide_from_robots": false,
                "icon_img": "https://www.redditstatic.com/avatars/defaults/v2/avatar_default_7.png",
                "id": "95ef",
                "is_blocked": false,
                "is_employee": false,
                "is_friend": false,
                "is_gold": false,
                "is_mod": false,
                "link_karma": 1,
                "name": "cristiano",
                "pref_show_snoovatar": false,
                "snoovatar_img": "",
                "snoovatar_size": null,
                "subreddit": {
                    "accept_followers": true,
                    "allowed_media_in_comments": [],
                    "banner_img": "",
                    "banner_size": null,
                    "community_icon": null,
                    "default_set": true,
                    "description": "",
                    "disable_contributor_requests": false,
                    "display_name": "u_cristiano",
                    "display_name_prefixed": "u/cristiano",
                    "free_form_reports": true,
                    "header_img": null,
                    "header_size": null,
                    "icon_color": "#E4ABFF",
                    "icon_img": "https://www.redditstatic.com/avatars/defaults/v2/avatar_default_7.png",
                    "icon_size": [
                        256,
                        256
                    ],
                    "is_default_banner": true,
                    "is_default_icon": true,
                    "key_color": "",
                    "link_flair_enabled": false,
                    "link_flair_position": "",
                    "name": "t5_3qm0f",
                    "over_18": false,
                    "previous_names": [],
                    "primary_color": "",
                    "public_description": "",
                    "quarantine": false,
                    "restrict_commenting": false,
                    "restrict_posting": true,
                    "show_media": true,
                    "submit_link_label": "",
                    "submit_text_label": "",
                    "subreddit_type": "user",
                    "subscribers": 0,
                    "title": "",
                    "url": "/user/cristiano/",
                    "user_is_banned": null,
                    "user_is_contributor": null,
                    "user_is_moderator": null,
                    "user_is_muted": null,
                    "user_is_subscriber": null
                },
                "total_karma": 1,
                "verified": true
            },
            "kind": "t2"
        }
    },
    "is_available": false,
    "success": true
}
```

---

# Docker 
## Usage 
```docker run -p 5000:5000 quanilo/handle-scraper:production```

## Development 
**After working on the project build docker with**   
    ```docker build -t [image_name]:[tagname] .  ```  
    ```docker push [image_name]:[tagname]```
