FROM php:8.2-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    libzip-dev \
    netcat-traditional

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip

# Install Redis extension
RUN pecl install redis && docker-php-ext-enable redis

# Get latest Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy composer.json first
COPY composer.json ./

# Install Laravel dependencies
RUN composer install --no-scripts --no-autoloader

# Copy all application files
COPY . .

# Install Laravel Reverb if not in composer.json
RUN composer require laravel/reverb --no-scripts

# Create necessary directories
RUN mkdir -p storage/framework/{cache,sessions,views} \
    && mkdir -p storage/logs \
    && mkdir -p bootstrap/cache

# Set temporary environment variables for build time
ENV APP_KEY=base64:temporary \
    BROADCAST_DRIVER=log \
    DB_CONNECTION=sqlite

# Generate autoloader
RUN composer dump-autoload --optimize

# Set permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html/storage \
    && chmod -R 755 /var/www/html/bootstrap/cache

# Make artisan executable
RUN chmod +x artisan

# Expose ports
EXPOSE 8000 8080

# Start script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
