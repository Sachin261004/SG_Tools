def get_available_countries():
    """
    Get a list of available regions (countries) and their region codes.
    Combines both topRegions and allRegions, with deduplication.
    """
    global auth_state

    if auth_state.session is None:
        auth_state.session = requests.Session()

    try:
        url = "https://pickyourtrail.com/api/region/search"
        response = auth_state.session.get(url)

        if response.status_code == 200:
            json_data = response.json()

            if json_data.get("status") == "SUCCESS":
                data = json_data.get("data", {})
                top_regions = data.get("topRegions", [])
                all_regions = data.get("allRegions", [])

                # Combine and deduplicate using regionCode
                combined = {region.get("regionCode"): region for region in top_regions + all_regions}

                countries = [
                    {
                        "name": region.get("region"),
                        "region_code": region.get("regionCode")
                    }
                    for region in combined.values()
                    if region.get("region") and region.get("regionCode")
                ]

                return {
                    "success": True,
                    "countries": countries
                }

            else:
                return {
                    "success": False,
                    "error": f"API status not SUCCESS: {json_data.get('status')}"
                }

        else:
            return {
                "success": False,
                "error": f"Failed to fetch countries: {response.status_code}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_region_info(region_code: str):
    """
    Get detailed information about a region using its region code.
    """
    global auth_state

    if auth_state.session is None:
        auth_state.session = requests.Session()

    try:
        url = f"https://pickyourtrail.com/api/region/{region_code}/info"
        response = auth_state.session.get(url)

        if response.status_code == 200:
            return {
                "success": True,
                "info": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Failed to fetch region info: {response.status_code}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }



def get_top_cities(min_days: int, max_days: int, preferred_month: str, region_code: str):
    """
    Get top city combos with comboId, cityIds, cityNames, and imageUrls.
    """
    global auth_state

    if auth_state.session is None:
        auth_state.session = requests.Session()

    url = "https://pickyourtrail.com/api/misc/getTopCities"

    payload = {
        "themeIds": ["5"],
        "interests": [4, 9, 12, 15, 19, 24, 27, 29, 31, 32, 33, 34, 36, 37, 38, 49, 51, 52, 66, 68, 79, 84],
        "buildPytItinerary": False,
        "new_activities": None,
        "comboId": None,
        "maxDays": max_days,
        "minDays": min_days,
        "preferredMonth": preferred_month,
        "region": region_code,
        "cities": []
    }

    try:
        response = auth_state.session.post(url, json=payload)

        if response.status_code == 200:
            json_data = response.json()
            combos = json_data.get("combos", [])

            combos = json_data.get("data", {}).get("combos", [])

            return {
                "success": True,
                "combos": combos    
            }

        else:
            return {
                "success": False,
                "error": f"Failed to fetch top cities: {response.status_code}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_preferred_languages():
    """
    Get available preferred languages
    """
    global auth_state
    
    if auth_state.session is None:
        auth_state.session = requests.Session()
    
    try:
        languages_url = "https://pickyourtrail.com/api/misc/preferredlanguages"
        response = auth_state.session.get(languages_url)
        
        if response.status_code == 200:
            return {
                "success": True,
                "languages": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Failed to get languages: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def check_login_status():
    """
    Check if user is already logged in by calling getUserDetails API
    Returns login status and user details if available
    """
    global auth_state
    
    print("🔍 Checking login status...")
    
    # Initialize session if not exists
    if auth_state.session is None:
        auth_state.session = requests.Session()
    
    try:
        user_details_response = auth_state.session.get("https://pickyourtrail.com/api/user/getUserDetails")
        print(f"📋 User details response: {user_details_response.status_code}")
        print(f"📄 Raw response: {user_details_response.text}")
        
        # Print the raw response text
        print(f"📄 Raw response: {user_details_response.text}")
        
        if user_details_response.status_code == 200:
            user_data = user_details_response.json()
            print(f"📋 User details data: {json.dumps(user_data, indent=2)}")
            
            # Check if user is logged in - adjust this condition based on actual API response structure
            is_logged_in = user_data.get("loggedIn", False) or user_data.get("data", {}).get("loggedIn", False)
            
            if is_logged_in:
                auth_state.user_logged_in = True
                auth_state.user_details = user_data
                print("✅ User is already logged in!")
                
                return {
                    "success": True,
                    "logged_in": True,
                    "user_details": user_data,
                    "message": "User is already authenticated"
                }
            else:
                auth_state.user_logged_in = False
                print("❌ User is not logged in")
                
                return {
                    "success": True,
                    "logged_in": False,
                    "message": "User needs authentication"
                }
        else:
            print(f"❌ Failed to check login status: {user_details_response.status_code}")
            return {
                "success": False,
                "logged_in": False,
                "error": f"Failed to check login status. Status Code: {user_details_response.status_code}",
                "message": "Unable to verify login status, proceeding with authentication"
            }
            
    except Exception as e:
        print(f"❌ Exception while checking login status: {str(e)}")
        return {
            "success": False,
            "logged_in": False,
            "error": str(e),
            "message": "Unable to verify login status, proceeding with authentication"
        }


def authenticate_user(mobile_number: str, name: str):
    """
    Step 1: Initiate OTP login process
    Returns session and data needed for OTP verification
    """
    global auth_state
    
    print(f"🔐 Starting authentication for {name} ({mobile_number})")
    
    # Start session to persist cookies if not already started
    if auth_state.session is None:
        auth_state.session = requests.Session()
    
    # Get cookies via user details API - use consistent domain
    try:
        user_details_response = auth_state.session.get("https://pickyourtrail.com/api/user/getUserDetails")
        print(f"📋 User details response: {user_details_response.status_code}")
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get user details: {str(e)}",
            "mobile": mobile_number,
            "name": name
        }
    
    # Trigger OTP login - use consistent domain
    otp_login_url = "https://pickyourtrail.com/api/user/otplogin"  # Changed from internal subdomain
    payload = {
        "mobileNumber": mobile_number,
        "countryPhoneCode": "+91",
        "name": name
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        otp_login_response = auth_state.session.post(otp_login_url, json=payload, headers=headers)
        
        print(f"📤 OTP request status: {otp_login_response.status_code}")
        print(f"📤 OTP request response: {otp_login_response.text}")
        
        if otp_login_response.status_code != 200:
            return {
                "success": False,
                "message": f"Failed to initiate OTP login. Status Code: {otp_login_response.status_code}",
                "mobile": mobile_number,
                "name": name,
                "response_text": otp_login_response.text
            }
        
        response_data = otp_login_response.json()
        auth_state.otp_data = response_data  # Store OTP data for verification
        
        return {
            "success": True,
            "message": "OTP sent successfully",
            "mobile": mobile_number,
            "name": name,
            "response_data": response_data
        }
            
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "mobile": mobile_number,
            "name": name
        }

def verify_otp(otp: str, language: str = None):
    """
    Step 2: Verify the OTP and complete authentication
    """
    global auth_state
    
    if not auth_state.session or not auth_state.otp_data:
        return {
            "success": False,
            "error": "No active authentication session. Please authenticate first."
        }
    
    print(f"🔑 Verifying OTP: {otp}")
    
    # Verify the OTP
    verify_url = "https://pickyourtrail.com/api/user/verifyotplogin"
    headers = {"Content-Type": "application/json"}
    
    try:
        # Take the data from authenticate_user response and replace only the otp field
        verify_data = auth_state.otp_data["data"].copy() 
        verify_data["otp"] = str(otp).zfill(6)
        verify_data["preferredLanguage"] = auth_state.preferred_language
        
        print(f"📤 Sending verification data: {json.dumps(verify_data, indent=2)}")
        
        verify_response = auth_state.session.post(verify_url, json=verify_data, headers=headers)
        
        print(f"📥 Response Status: {verify_response.status_code}")
        print(f"📥 Response Text: {verify_response.text}")
        
        if verify_response.status_code == 200:
            try:
                response_json = verify_response.json()
                print(f"📥 Response JSON: {json.dumps(response_json, indent=2)}")
                
                # Check for the specific success condition: status == "VERIFIED"
                if response_json.get("status") == "VERIFIED":
                    print("✅ Authentication successful!")
                    auth_state.user_logged_in = True
                    auth_state.user_details = response_json
                    return {
                        "success": True,
                        "message": "Authentication completed successfully!",
                        "response": response_json
                    }
                else:
                    print(f"❌ Authentication failed - Status: {response_json.get('status')}")
                    return {
                        "success": False,
                        "error": f"OTP verification failed: {response_json.get('message', 'Invalid OTP or status not VERIFIED')}",
                        "response": response_json
                    }
                    
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON response")
                return {
                    "success": False,
                    "error": "Invalid JSON response from server",
                    "response": verify_response.text
                }
        else:
            print(f"❌ HTTP Error: {verify_response.status_code}")
            return {
                "success": False,
                "error": f"OTP verification failed. Status Code: {verify_response.status_code}",
                "response": verify_response.text
            }
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return {
            "success": False,
            "error": f"Error during OTP verification: {str(e)}"
        }


def create_and_cost_itinerary(preferred_month: str, year: str, day: str, date: str, 
                             duration_of_holidays: int, travel_with: str, adult_count: int,
                             region_code: str, cities: list,
                             child_ages: list = None, nationality: str = "IN"):
    """
    Combined function that creates itinerary AND calculates costs in one step
    Requires user to be authenticated first (either via OTP or pre-existing login)
    """
    global auth_state
    
    if auth_state.session is None:
        return {
            "success": False,
            "error": "User not authenticated. Please authenticate first using check_login_status or authenticate_user and verify_otp functions."
        }
    
    # Check if user is authenticated (either via login check or OTP verification)
    if not auth_state.user_logged_in:
        return {
            "success": False,
            "error": "User not authenticated. Please complete authentication first."
        }
    
    if child_ages is None:
        child_ages = []
    
    print(f"🚀 Starting create_and_cost_itinerary for {duration_of_holidays} days in {preferred_month}")
    
    # Step 1: Create Itinerary
    # Map duration to min-max bracket
    if 3 <= duration_of_holidays <= 5:
        min_days, max_days = 3, 5
    elif 6 <= duration_of_holidays <= 8:
        min_days, max_days = 6, 8
    elif 9 <= duration_of_holidays <= 11:
        min_days, max_days = 9, 11
    elif 12 <= duration_of_holidays <= 15:
        min_days, max_days = 12, 15
    else:
        return {"error": "Duration must be between 3 and 15 days"}

    data = {
        "cities": cities,
        "maxDays": max_days,
        "minDays": min_days,
        "preferredMonth": preferred_month.upper(),
        "region": region_code,
        "interests": [
            4, 9, 12, 15, 19, 24, 27, 29, 31, 32, 33, 34, 36,
            37, 38, 49, 51, 52, 66, 68, 79, 84
        ],
        "themes": ["A bit of everything"],
        "themeIds": ["5"],
        "cityActivityMap": [],
        "leadSource": {
            "cpid": None,
            "landingPage": "https://pickyourtrail.com/",
            "searchKeyWords": False,
            "keyword": "",
            "url": "https://pickyourtrail.com/",
            "deviceType": "Desktop",
            "prodType": "PDG",
            "ipInfo": {},
            "lastRoute": "",
            "campaign": "",
            "unityEnabled": "false",
            "regionCode": region_code,
            "month": preferred_month,
            "year": year,
            "day": day,
            "date": date,
            "dc": "$$$",
            "dcName": "No Flight",
            "min": str(min_days),
            "max": str(max_days),
            "travelWith": travel_with.upper(),
            "pax": f"a{adult_count}" + (f"c{len(child_ages)}" if child_ages else "")
        },
        "buildPytItinerary": False,
        "new_activities": None,
        "comboId": None
    }

    # Create itinerary using authenticated session
    try:
        headers = {"Content-Type": "application/json"}
        response = auth_state.session.post("https://pickyourtrail.com/api/itinerary/create", json=data, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        itinerary_id = response_data.get("data", {}).get("itineraryId")

        if not itinerary_id:
            return {"error": "itineraryId not found in response"}

        print(f"✅ Successfully created itinerary. ID: {itinerary_id}")
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}
    except ValueError as ve:
        return {"error": f"Error in response data: {ve}"}

    # Step 2: Immediately cost the itinerary
    print(f"💰 Starting costing calculation for itinerary {itinerary_id}")
    
    # Get travel type mapping
    travel_mapping = get_travel_type_mapping(travel_with)
    travel_type = travel_mapping["travel_type"]
    trip_type = travel_mapping["trip_type"]

    # Parse departure date to get components
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d/%b/%Y")
        month = date_obj.strftime("%B")
        year_from_date = str(date_obj.year)
        day_from_date = str(date_obj.day)
    except ValueError:
        return {"error": "Invalid departure_date format. Expected YYYY-MM-DD"}

    # Trigger costing using authenticated session
    calculate_url = f"https://pickyourtrail.com/api/itinerary/{itinerary_id}/calculateCost"
    calculate_payload = {
        "costingConfig": {
            "arrivalAirport": "",
            "departureAirport": "$$$",
            "departureDate": formatted_date,
            "hotelGuestRoomConfigurations": [{"adultCount": adult_count, "childAges": child_ages}],
            "nationality": nationality,
            "travelType": travel_type,
            "tripType": trip_type
        },
        "costingType": "RECOST",
        "flightsBookedByUserAlready": False,
        "itineraryId": itinerary_id,
        "name": "",
        "leadSource": {
            "cpid": None,
            "landingPage": "https://pickyourtrail.com/",
            "searchKeyWords": False,
            "keyword": "",
            "url": "https://pickyourtrail.com/",
            "deviceType": "Desktop",
            "prodType": "PDG",
            "ipInfo": {},
            "lastRoute": "",
            "campaign": "",
            "unityEnabled": "false",
            "regionCode": "sin",
            "month": month,
            "year": year_from_date,
            "day": day_from_date,
            "date": date,
            "dc": "$$$",
            "dcName": "No Flight",
            "min": "3",
            "max": "15",
            "travelWith": travel_type,
            "pax": f"a{adult_count}" + (f"c{len(child_ages)}" if child_ages else "")
        }
    }

    headers = {"Content-Type": "application/json"}
    calculate_response = auth_state.session.post(calculate_url, json=calculate_payload, headers=headers)
    
    if calculate_response.status_code != 200:
        return {"error": f"Failed to trigger costing calculation: {calculate_response.text}"}

    # Check costing status (wait for calculation to complete)
    costing_status_url = f"https://pickyourtrail.com/api/itinerary/{itinerary_id}/checkCostingStatus?flight-details=false"
    max_attempts = 15
    attempt = 0
    
    print(f"⏳ Checking costing status for itinerary {itinerary_id}...")
    
    while attempt < max_attempts:
        status_response = auth_state.session.get(costing_status_url, headers=headers)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"Costing status check {attempt + 1}: {status_data}")
            
            if status_data.get("status") == "SUCCESS" and status_data.get("data") == "COMPLETE":
                print("✅ Costing calculation completed successfully!")
                break
        else:
            print(f"Status check failed with code: {status_response.status_code}")
            
        time.sleep(3)  # Wait 3 seconds before next check
        attempt += 1
    
    if attempt >= max_attempts:
        return {"error": "Costing calculation timed out after multiple attempts"}

    # Step 3: Immediately fetch detailed itinerary after costing
    print(f"📋 Fetching detailed itinerary for {itinerary_id}")
    
    details_url = f"https://pickyourtrail.com/api/itinerary/{itinerary_id}/details"
    details_response = auth_state.session.get(details_url, headers=headers)
    
    if details_response.status_code != 200:
        return {"error": f"Failed to fetch itinerary details: {details_response.text}"}

    try:
        itinerary_details = details_response.json()
        
        # Get cost summary
        cost_summary_url = f"https://pickyourtrail.com/api/itinerary/{itinerary_id}/summary"
        cost_response = auth_state.session.get(cost_summary_url, headers=headers)
        
        cost_data = {}
        if cost_response.status_code == 200:
            cost_summary = cost_response.json()
            if "data" in cost_summary and "pricing" in cost_summary["data"]:
                pricing = cost_summary["data"]["pricing"]
                cost_data = {
                    "base_amount": pricing.get("baseAmount", 0),
                    "tcs_amount": pricing.get("tcsAmount", 0),
                    "total_amount": pricing.get("totalAmount", 0)
                }

        customize_url = f"https://pickyourtrail.com/customize/sin/view/{itinerary_id}"
        
        return {
            "success": True,
            "itineraryId": itinerary_id,
            "customizeUrl": customize_url,
            "costing_complete": True,
            "cost_data": cost_data,
            "itinerary_details": itinerary_details,
            "message": "Itinerary created, costed, and detailed information fetched successfully!"
        }
        
    except Exception as e:
        return {"error": f"Error processing itinerary details: {str(e)}"}
