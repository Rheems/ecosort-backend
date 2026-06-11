from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User, UserPromptSettings
import pytz
import random


PROMPT_MESSAGES = {
    'plastic': "🌿 Ecosort Tip: Rinse your plastic bottles and crush them flat before sorting. Clean plastic earns ₦240-350/kg! Reply GUIDE PLASTIC for the full guide.",
    'glass': "🌿 Ecosort Tip: Store glass bottles in a box — never a bag. If one breaks, wrap in newspaper and warn your collector. Reply GUIDE GLASS to learn more.",
    'metal': "🌿 Ecosort Tip: Aluminium cans earn ₦700/kg! Crush them flat. NEVER include spray cans — fire risk! Reply GUIDE METAL for full guide.",
    'paper': "🌿 Ecosort Tip: WET PAPER PAYS NOTHING! Keep your cardboard dry and elevated off the ground. Reply GUIDE PAPER to learn more.",
    'organic': "🌿 Ecosort Tip: Use 3 bags — Recyclables, Organic and General waste. Food residue ruins recyclable batches! Reply GUIDE ORGANIC for the full guide.",
    'ewaste': "🌿 Ecosort Tip: NEVER burn e-waste — it releases toxic chemicals. Remove your SIM before giving old phones. Reply GUIDE EWASTE to learn more.",
}

CATEGORIES = ['plastic', 'glass', 'metal', 'paper', 'organic', 'ewaste']


class Command(BaseCommand):
    help = 'Send weekly educational prompts to users via SMS'

    def handle(self, *args, **kwargs):
        wat = pytz.timezone('Africa/Lagos')
        now = timezone.now().astimezone(wat)
        today = now.date()
        weekday = today.weekday()  # 0=Mon, 1=Tue... 6=Sun

        # Only send on Mon(0), Wed(2), Fri(4)
        if weekday not in [0, 2, 4]:
            self.stdout.write('Not a prompt day — skipping.')
            return

        users = User.objects.filter(
            phone_number__isnull=False
        ).exclude(phone_number='')

        sent_count = 0
        skipped_count = 0

        for user in users:
            try:
                settings_obj, _ = UserPromptSettings.objects.get_or_create(user=user)

                # Check if stopped
                if not settings_obj.is_active or settings_obj.frequency == 'stopped':
                    skipped_count += 1
                    continue

                # Check if snoozed
                if settings_obj.snoozed_until and now < settings_obj.snoozed_until:
                    skipped_count += 1
                    continue

                # Check frequency — after 14 days switch to 1x/week (Monday only)
                days_since_registration = (today - settings_obj.registered_at.date()).days
                if days_since_registration > 14:
                    settings_obj.frequency = '1x_week'
                    settings_obj.save()
                    if weekday != 0:  # Only Monday
                        skipped_count += 1
                        continue

                # Pick next category — rotate, no repeat within 6 messages
                last_cat = settings_obj.last_category_sent
                available = [c for c in CATEGORIES if c != last_cat]
                category = random.choice(available)

                message = PROMPT_MESSAGES[category]

                # Send via Africa's Talking
                from myapp.services.africastalking_service import sms
                sms.send(message, [user.phone_number])

                # Update settings
                settings_obj.last_prompt_sent = now
                settings_obj.last_category_sent = category
                settings_obj.save()

                sent_count += 1
                self.stdout.write(f"✅ Sent to {user.phone_number} — {category}")

            except Exception as e:
                self.stdout.write(f"❌ Failed for {user.phone_number}: {str(e)}")

        self.stdout.write(
            self.style.SUCCESS(f'\n🌿 Prompts sent: {sent_count} | Skipped: {skipped_count}')
        )