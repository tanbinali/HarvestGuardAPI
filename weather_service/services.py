import requests
from datetime import datetime, timedelta
from django.core.cache import cache
from decouple import config

class WeatherService:
    """Handle weather API integration"""
    
    # Bangladeshi Upazilas mapping (sample)
    UPAZILAS = {
        'DHAKA': {'lat': 23.8103, 'lng': 90.4125},
        'CHITTAGONG': {'lat': 22.3569, 'lng': 91.7832},
        'SYLHET': {'lat': 24.8949, 'lng': 91.8687},
        'RAJSHAHI': {'lat': 24.3745, 'lng': 88.6042},
        'KHULNA': {'lat': 22.8046, 'lng': 89.5680},
        'BARISHAL': {'lat': 22.7010, 'lng': 90.3535},
        'RANGPUR': {'lat': 25.7439, 'lng': 89.2752},
        'MYMENSINGH': {'lat': 24.7471, 'lng': 90.4203},
    }
    
    def __init__(self):
        self.api_key = config('OPENWEATHERMAP_API_KEY', default='your-api-key')
        self.base_url = 'https://api.openweathermap.org/data/2.5'
    
    def get_forecast(self, location):
        """Fetch 5-day forecast for a location"""
        cache_key = f'weather_{location}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        if location not in self.UPAZILAS:
            return self._get_mock_forecast(location)
        
        coords = self.UPAZILAS[location]
        try:
            response = requests.get(
                f"{self.base_url}/forecast",
                params={
                    'lat': coords['lat'],
                    'lon': coords['lng'],
                    'appid': self.api_key,
                    'units': 'metric'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                forecast_data = self._parse_forecast(response.json())
                cache.set(cache_key, forecast_data, 3600)  # Cache for 1 hour
                return forecast_data
        except Exception as e:
            print(f"Weather API error: {e}")
        
        return self._get_mock_forecast(location)
    
    def _parse_forecast(self, data):
        """Parse OpenWeatherMap forecast response"""
        forecasts = []
        for item in data['list'][:40:8]:  # Every 3 days
            dt = datetime.fromtimestamp(item['dt'])
            forecasts.append({
                'date': dt.date().isoformat(),
                'temperature': item['main']['temp'],
                'humidity': item['main']['humidity'],
                'rainfall_probability': item.get('pop', 0) * 100,
                'wind_speed': item['wind']['speed'],
                'description': item['weather']['main']
            })
        return forecasts
    
    def _get_mock_forecast(self, location):
        """Fallback mock forecast when API unavailable"""
        forecasts = []
        base_temp = 28 + hash(location) % 5
        for i in range(5):
            date = (datetime.now() + timedelta(days=i)).date()
            forecasts.append({
                'date': date.isoformat(),
                'temperature': base_temp + (i % 3),
                'humidity': 65 + (hash(location + str(i)) % 20),
                'rainfall_probability': (hash(location + str(i)) % 70),
                'wind_speed': 5 + (hash(location) % 10),
                'description': 'Partly Cloudy'
            })
        return forecasts
    
    def get_bangla_advisory(self, batch, forecast):
        """Generate Bangla weather advisory based on forecast"""
        advisories = []
        
        # Check rainfall risk
        high_rain_days = sum(1 for f in forecast if f['rainfall_probability'] > 75)
        if high_rain_days >= 2:
            advisories.append("আগামী কয়েক দিন বৃষ্টির সম্ভাবনা বেশি। ধান ঢেকে রাখুন এবং ভালোভাবে বায়ু চলাচল নিশ্চিত করুন।")
        
        # Check temperature
        avg_temp = sum(f['temperature'] for f in forecast) / len(forecast)
        if avg_temp > 32:
            advisories.append(f"তাপমাত্রা অত্যধিক ({avg_temp:.0f}°C)। ধানের ছাদে ছায়া দিন এবং নিয়মিত আর্দ্রতা পরীক্ষা করুন।")
        
        # Check humidity
        avg_humidity = sum(f['humidity'] for f in forecast) / len(forecast)
        if avg_humidity > 80:
            advisories.append("অত্যধিক আর্দ্রতা ছাঁচের ঝুঁকি বাড়ায়। ভেন্টিলেশন বৃদ্ধি করুন।")
        
        if not advisories:
            advisories.append("আবহাওয়া পরিস্থিতি স্বাভাবিক। নিয়মিত পর্যবেক্ষণ চালিয়ে যান।")
        
        return advisories


class RiskPredictionService:
    """Calculate risk and ETCL (Estimated Time to Critical Loss)"""
    
    def calculate_etcl(self, batch, weather_forecast):
        """Calculate ETCL based on weather conditions"""
        risk_factors = []
        etcl_hours = 999  # Default high value
        
        # Analyze temperature and humidity combination
        for forecast in weather_forecast:
            temp = forecast['temperature']
            humidity = forecast['humidity']
            
            # High temp + high humidity = mold risk
            if temp > 28 and humidity > 75:
                risk_factors.append("উচ্চ তাপমাত্রা এবং আর্দ্রতা - ছাঁচের ঝুঁকি")
                etcl_hours = min(etcl_hours, 48)
            
            # High rainfall risk
            if forecast['rainfall_probability'] > 80:
                risk_factors.append("বৃষ্টির উচ্চ ঝুঁকি - নিরাপদ সংরক্ষণ প্রয়োজন")
                etcl_hours = min(etcl_hours, 24)
        
        # Determine risk level
        if etcl_hours <= 24:
            risk_level = 'CRITICAL'
        elif etcl_hours <= 48:
            risk_level = 'HIGH'
        elif etcl_hours <= 120:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Generate recommendations
        recommendations = self._get_recommendations(risk_level, risk_factors)
        
        return {
            'etcl_hours': etcl_hours,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': recommendations
        }
    
    def _get_recommendations(self, risk_level, risk_factors):
        """Generate actionable recommendations in Bangla"""
        recommendations = []
        
        if risk_level == 'CRITICAL':
            recommendations.append("জরুরি: আজই ধান কাটুন বা গুদাম দিয়ে সম্পূর্ণভাবে ঢেকে দিন।")
            recommendations.append("নিয়মিত বায়ু চলাচল এবং আর্দ্রতা পর্যবেক্ষণ শুরু করুন।")
        elif risk_level == 'HIGH':
            recommendations.append("ধান ঢেকে রাখুন এবং অতিরিক্ত বায়ু চলাচলের ব্যবস্থা করুন।")
            recommendations.append("প্রতি ২ ঘণ্টায় আর্দ্রতা পরীক্ষা করুন।")
        elif risk_level == 'MEDIUM':
            recommendations.append("নিয়মিত পর্যবেক্ষণ চালিয়ে যান।")
            recommendations.append("ভাল বায়ু চলাচল নিশ্চিত করুন।")
        else:
            recommendations.append("বর্তমান পরিস্থিতি নিরাপদ। স্ট্যান্ডার্ড সংরক্ষণ পদ্ধতি অনুসরণ করুন।")
        
        return recommendations
