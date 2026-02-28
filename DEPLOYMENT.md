# Deployment Checklist

Use this checklist to deploy your Energy Dashboard to production.

## Pre-Deployment

### Security
- [ ] Change `SECRET_KEY` from default value
- [ ] Set `DEBUG = False` in production
- [ ] Use HTTPS for Home Assistant connection
- [ ] Store sensitive credentials in environment variables
- [ ] Add `.env` file to `.gitignore`
- [ ] Review and restrict network access

### Configuration
- [ ] Set correct `HA_URL` for your Home Assistant instance
- [ ] Generate and configure long-lived access token
- [ ] Configure correct `ELECTRICITY_RATE` for your region
- [ ] Set appropriate `CURRENCY_SYMBOL`
- [ ] Adjust `CACHE_TTL` based on your needs
- [ ] Set `REFRESH_INTERVAL` for auto-refresh

### Testing
- [ ] Test Home Assistant connection
- [ ] Verify power sensors are detected
- [ ] Check all five pages load correctly
- [ ] Test dark/light mode toggle
- [ ] Verify charts render properly
- [ ] Test on mobile devices
- [ ] Check historical data retrieval

## Deployment Options

### Option 1: Direct Python

```bash
# Production run with Gunicorn
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Checklist:
- [ ] Install Gunicorn: `pip3 install gunicorn`
- [ ] Set worker count based on CPU cores
- [ ] Configure log files
- [ ] Set up systemd service (Linux)
- [ ] Configure firewall rules

### Option 2: Docker

```bash
# Build image
docker build -t energy-dashboard .

# Run container
docker run -d \
  -p 5000:5000 \
  -e HA_URL="http://homeassistant:8123" \
  -e HA_TOKEN="your-token" \
  -e ELECTRICITY_RATE="0.12" \
  --name energy-dashboard \
  energy-dashboard
```

Checklist:
- [ ] Create Dockerfile
- [ ] Build Docker image
- [ ] Test container locally
- [ ] Configure environment variables
- [ ] Set up volume for logs
- [ ] Configure Docker network

### Option 3: Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name energy.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Checklist:
- [ ] Install Nginx
- [ ] Create site configuration
- [ ] Test configuration: `nginx -t`
- [ ] Enable site
- [ ] Configure SSL/TLS (Let's Encrypt)
- [ ] Set up automatic certificate renewal

## Post-Deployment

### Monitoring
- [ ] Set up log rotation
- [ ] Configure log monitoring/alerting
- [ ] Monitor disk space usage
- [ ] Check memory usage
- [ ] Monitor API response times

### Maintenance
- [ ] Document backup procedures
- [ ] Set up automated backups
- [ ] Plan update strategy
- [ ] Document rollback procedures
- [ ] Create maintenance schedule

### Performance
- [ ] Monitor cache hit rates
- [ ] Adjust cache TTL if needed
- [ ] Check API call frequency
- [ ] Optimize refresh intervals
- [ ] Monitor database size (Home Assistant)

### Access
- [ ] Configure authentication (if needed)
- [ ] Set up user accounts
- [ ] Document access procedures
- [ ] Share access credentials securely

## Systemd Service (Linux)

Create `/etc/systemd/system/energy-dashboard.service`:

```ini
[Unit]
Description=Energy Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/energy-dashboard
Environment="HA_URL=http://homeassistant:8123"
Environment="HA_TOKEN=your-token"
Environment="ELECTRICITY_RATE=0.12"
ExecStart=/usr/bin/python3 /opt/energy-dashboard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Checklist:
- [ ] Create service file
- [ ] Set correct paths and user
- [ ] Configure environment variables
- [ ] Reload systemd: `systemctl daemon-reload`
- [ ] Enable service: `systemctl enable energy-dashboard`
- [ ] Start service: `systemctl start energy-dashboard`
- [ ] Check status: `systemctl status energy-dashboard`

## SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d energy.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

Checklist:
- [ ] Install Certbot
- [ ] Configure DNS A record
- [ ] Obtain SSL certificate
- [ ] Test HTTPS access
- [ ] Verify auto-renewal

## Backup Strategy

### What to Backup
- [ ] Configuration files (`config.py`, `.env`)
- [ ] Custom templates (if modified)
- [ ] Custom CSS/JS (if modified)
- [ ] Log files (if needed for analysis)

### Backup Commands
```bash
# Configuration backup
tar -czf energy-dashboard-config-$(date +%Y%m%d).tar.gz config.py

# Full backup
tar -czf energy-dashboard-backup-$(date +%Y%m%d).tar.gz \
  --exclude='logs' \
  --exclude='__pycache__' \
  /opt/energy-dashboard
```

Checklist:
- [ ] Set up automated backups
- [ ] Test backup restoration
- [ ] Store backups securely
- [ ] Document backup locations

## Update Procedure

1. Backup current installation
2. Stop the service
3. Pull latest changes
4. Update dependencies: `pip3 install -r requirements.txt --upgrade`
5. Test configuration
6. Start the service
7. Verify functionality

Checklist:
- [ ] Create update runbook
- [ ] Test update in staging
- [ ] Schedule maintenance window
- [ ] Notify users
- [ ] Perform update
- [ ] Verify all features working

## Troubleshooting

### Service Won't Start
- Check logs: `journalctl -u energy-dashboard -n 50`
- Verify Python path
- Check file permissions
- Verify Home Assistant accessibility

### High Memory Usage
- Reduce cache TTL values
- Decrease refresh interval
- Limit number of devices
- Check for memory leaks in logs

### Connection Errors
- Verify Home Assistant URL
- Check token validity
- Test network connectivity: `curl $HA_URL/api/`
- Check firewall rules

## Health Checks

Create a monitoring endpoint or script:

```bash
#!/bin/bash
# health-check.sh

response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/overview)

if [ $response -eq 200 ]; then
    echo "OK: Energy Dashboard is running"
    exit 0
else
    echo "ERROR: Energy Dashboard returned $response"
    exit 1
fi
```

Checklist:
- [ ] Create health check script
- [ ] Set up monitoring (Nagios, Zabbix, etc.)
- [ ] Configure alerts
- [ ] Test alerting

## Security Hardening

- [ ] Run as non-root user
- [ ] Restrict file permissions
- [ ] Enable firewall (ufw, iptables)
- [ ] Keep dependencies updated
- [ ] Review logs regularly
- [ ] Implement rate limiting
- [ ] Use fail2ban for brute force protection

## Documentation

- [ ] Document deployment steps taken
- [ ] Record configuration decisions
- [ ] Document custom modifications
- [ ] Create runbook for common tasks
- [ ] Share access information securely

## Final Verification

- [ ] All pages load without errors
- [ ] Data updates in real-time
- [ ] Charts render correctly
- [ ] Dark/light mode works
- [ ] Mobile responsive
- [ ] Logs are clean
- [ ] Performance is acceptable
- [ ] Backups are configured
- [ ] Monitoring is active

## Go Live!

Once all items are checked:
- [ ] Announce to users
- [ ] Monitor closely for 24-48 hours
- [ ] Be ready to rollback if needed
- [ ] Gather user feedback
- [ ] Plan improvements

Congratulations on your deployment!
