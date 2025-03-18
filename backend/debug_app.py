from app import app, db, User
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('flask.app')
logger.setLevel(logging.DEBUG)

# Enhance the app with debugging
def setup_debug_app():
    # Add request debugging
    @app.before_request
    def log_request_info():
        from flask import request
        logger.debug('Request Method: %s', request.method)
        logger.debug('Request URL: %s', request.url)
        logger.debug('Request Headers: %s', request.headers)
        logger.debug('Request Form Data: %s', request.form)
    
    # Add response debugging
    @app.after_request
    def log_response_info(response):
        logger.debug('Response Status: %s', response.status)
        logger.debug('Response Headers: %s', response.headers)
        return response

if __name__ == '__main__':
    setup_debug_app()
    
    # Run the app with enhanced debugging
    app.run(debug=True, use_reloader=False) 