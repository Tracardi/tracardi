from tracardi.domain.profile_data import ProfileMedia, ProfilePII, ProfileLanguage, ProfileSocialMedia, \
    ProfileEducation, ProfileCivilData, ProfileAttribute, ProfileIdentifier, ProfileContact, ProfileEmail, ProfilePhone, \
    ProfileContactApp, ProfileContactAddress, ProfileJob, ProfileCompany, ProfilePreference, ProfileLoyalty, \
    ProfileLoyaltyCard

from tracardi.domain.entity import Entity, PrimaryEntity
from tracardi.domain.event import Event, EventSession, EventData, EventEc, EventProduct, EventProductVariant, \
    EventCheckout, EventOrder, Money, EventMessage, EventPayment, EventCreditCard, EventMarketing, EventPromotion, \
    EventJourney, Tags
from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.geo import Geo, Country
from tracardi.domain.marketing import UTM
from tracardi.domain.metadata import Device, OS, Application, Hit
from tracardi.domain.time import EventTime
from tracardi.service.storage.mysql.utils.serilizer import to_json
from tracardi.service.storage.starrocks.schema.table import EventTable


def map_to_event_table(event: Event) -> EventTable:
    return EventTable(
        id=event.id,
        name=event.name,
        metadata_aux=event.metadata.aux,
        metadata_time_insert=event.metadata.time.insert,
        metadata_time_create=event.metadata.time.create,
        metadata_time_process_time=event.metadata.time.process_time,
        metadata_time_total_time=event.metadata.time.total_time,
        metadata_status=event.metadata.status,
        metadata_channel=event.metadata.channel,
        metadata_ip=event.metadata.ip,
        # metadata_processed_by_rules=event.metadata.processed_by.rules,
        # metadata_processed_by_flows=event.metadata.processed_by.flows,
        # metadata_processed_by_third_party=event.metadata.processed_by.third_party,
        metadata_profile_less=event.metadata.profile_less,
        metadata_valid=event.metadata.valid,
        metadata_warning=event.metadata.warning,
        metadata_error=event.metadata.error,
        metadata_merge=event.metadata.merge,
        metadata_instance_id=event.metadata.instance.id,
        metadata_debug=event.metadata.debug,
        type=event.type,
        request=event.request,
        source_id=event.source.id,
        device_name=event.device.name if event.device else None,
        device_brand=event.device.brand if event.device else None,
        device_model=event.device.model if event.device else None,
        device_ip=event.device.ip if event.device else None,
        device_type=event.device.type if event.device else None,
        device_touch=event.device.touch if event.device else None,
        device_resolution=event.device.resolution if event.device else None,
        device_color_depth=event.device.color_depth if event.device else None,
        device_orientation=event.device.orientation if event.device else None,
        device_geo_country_name=event.device.geo.country.name if event.device and event.device.geo and event.device.geo.country else None,
        device_geo_country_code=event.device.geo.country.code if event.device and event.device.geo and event.device.geo.country else None,
        device_geo_county=event.device.geo.county if event.device and event.device.geo else None,
        device_geo_city=event.device.geo.city if event.device and event.device.geo else None,
        device_geo_latitude=event.device.geo.latitude if event.device and event.device.geo else None,
        device_geo_longitude=event.device.geo.longitude if event.device and event.device.geo else None,
        device_geo_location=event.device.geo.location if event.device and event.device.geo else None,
        device_geo_postal=event.device.geo.postal if event.device and event.device.geo else None,
        os_name=event.os.name if event.os else None,
        os_version=event.os.version if event.os else None,
        app_type=event.app.type if event.app else None,
        app_bot=event.app.bot if event.app else None,
        app_name=event.app.name if event.app else None,
        app_version=event.app.version if event.app else None,
        app_language=event.app.language if event.app else None,
        app_resolution=event.app.resolution if event.app else None,
        hit_name=event.hit.name if event.hit else None,
        hit_url=event.hit.url if event.hit else None,
        hit_referer=event.hit.referer if event.hit else None,
        hit_query=event.hit.query if event.hit else None,
        hit_category=event.hit.category if event.hit else None,
        hit_id=event.hit.id if event.hit else None,
        utm_source=event.utm.source if event.utm else None,
        utm_medium=event.utm.medium if event.utm else None,
        utm_campaign=event.utm.campaign if event.utm else None,
        utm_term=event.utm.term if event.utm else None,
        utm_content=event.utm.content if event.utm else None,
        session_id=event.session.id if event.session else None,
        session_start=event.session.start if event.session else None,
        session_duration=event.session.duration if event.session else None,
        session_tz=event.session.tz if event.session else None,
        profile_id=event.profile.id if event.profile else None,
        entity_id=event.entity_id,
        aux=event.aux,
        trash=event.trash,
        config=event.config,
        context=event.context,
        properties=event.properties,
        traits=event.traits,
        data_media_image=event.data.media.image if event.data and event.data.media else None,
        data_media_webpage=event.data.media.webpage if event.data and event.data.media else None,
        data_media_social_twitter=event.data.media.social.twitter if event.data and event.data.media and event.data.media.social else None,
        data_media_social_facebook=event.data.media.social.facebook if event.data and event.data.media and event.data.media.social else None,
        data_media_social_youtube=event.data.media.social.youtube if event.data and event.data.media and event.data.media.social else None,
        data_media_social_instagram=event.data.media.social.instagram if event.data and event.data.media and event.data.media.social else None,
        data_media_social_tiktok=event.data.media.social.tiktok if event.data and event.data.media and event.data.media.social else None,
        data_media_social_linkedin=event.data.media.social.linkedin if event.data and event.data.media and event.data.media.social else None,
        data_media_social_reddit=event.data.media.social.reddit if event.data and event.data.media and event.data.media.social else None,
        data_media_social_other=event.data.media.social.other if event.data and event.data.media and event.data.media.social else None,
        data_pii_firstname=event.data.pii.firstname if event.data and event.data.pii else None,
        data_pii_lastname=event.data.pii.lastname if event.data and event.data.pii else None,
        data_pii_display_name=event.data.pii.display_name if event.data and event.data.pii else None,
        data_pii_birthday=event.data.pii.birthday if event.data and event.data.pii else None,
        data_pii_language_native=event.data.pii.language.native if event.data and event.data.pii and event.data.pii.language else None,
        data_pii_language_spoken=event.data.pii.language.spoken if event.data and event.data.pii and event.data.pii.language else None,
        data_pii_gender=event.data.pii.gender if event.data and event.data.pii else None,
        data_pii_education_level=event.data.pii.education.level if event.data and event.data.pii and event.data.pii.education else None,
        data_pii_civil_status=event.data.pii.civil.status if event.data and event.data.pii and event.data.pii.civil else None,
        data_pii_attributes_height=event.data.pii.attributes.height if event.data and event.data.pii and event.data.pii.attributes else None,
        data_pii_attributes_weight=event.data.pii.attributes.weight if event.data and event.data.pii and event.data.pii.attributes else None,
        data_pii_attributes_shoe_number=event.data.pii.attributes.shoe_number if event.data and event.data.pii and event.data.pii.attributes else None,
        data_identifier_id=event.data.identifier.id if event.data and event.data.identifier else None,
        data_identifier_pk=event.data.identifier.pk if event.data and event.data.identifier else None,
        data_identifier_badge=event.data.identifier.badge if event.data and event.data.identifier else None,
        data_identifier_passport=event.data.identifier.passport if event.data and event.data.identifier else None,
        data_identifier_credit_card=event.data.identifier.credit_card if event.data and event.data.identifier else None,
        data_identifier_token=event.data.identifier.token if event.data and event.data.identifier else None,
        data_identifier_coupons=event.data.identifier.coupons if event.data and event.data.identifier else None,
        data_contact_email_main=event.data.contact.email.main if event.data and event.data.contact and event.data.contact.email else None,
        data_contact_email_private=event.data.contact.email.private if event.data and event.data.contact and event.data.contact.email else None,
        data_contact_email_business=event.data.contact.email.business if event.data and event.data.contact and event.data.contact.email else None,
        data_contact_phone_main=event.data.contact.phone.main if event.data and event.data.contact and event.data.contact.phone else None,
        data_contact_phone_business=event.data.contact.phone.business if event.data and event.data.contact and event.data.contact.phone else None,
        data_contact_phone_mobile=event.data.contact.phone.mobile if event.data and event.data.contact and event.data.contact.phone else None,
        data_contact_phone_whatsapp=event.data.contact.phone.whatsapp if event.data and event.data.contact and event.data.contact.phone else None,
        data_contact_app_whatsapp=event.data.contact.app.whatsapp if event.data and event.data.contact and event.data.contact.app else None,
        data_contact_app_discord=event.data.contact.app.discord if event.data and event.data.contact and event.data.contact.app else None,
        data_contact_app_slack=event.data.contact.app.slack if event.data and event.data.contact and event.data.contact.app else None,
        data_contact_app_twitter=event.data.contact.app.twitter if event.data and event.data.contact and event.data.contact.app else None,
        data_contact_app_telegram=event.data.contact.app.telegram if event.data and event.data.contact and event.data.contact.app else None,
        data_contact_app_wechat=event.data.contact.app.wechat if event.data and event.data.contact and event.data.contact.app else None,
        data_contact_app_viber=event.data.contact.app.viber if event.data and event.data.contact and event.data.contact.app else None,
        data_contact_app_signal=event.data.contact.app.signal if event.data and event.data.contact and event.data.contact.app else None,
        data_contact_app_other=event.data.contact.app.other if event.data and event.data.contact and event.data.contact.app else None,
        data_contact_address_town=event.data.contact.address.town if event.data and event.data.contact and event.data.contact.address else None,
        data_contact_address_county=event.data.contact.address.county if event.data and event.data.contact and event.data.contact.address else None,
        data_contact_address_country=event.data.contact.address.country if event.data and event.data.contact and event.data.contact.address else None,
        data_contact_address_postcode=event.data.contact.address.postcode if event.data and event.data.contact and event.data.contact.address else None,
        data_contact_address_street=event.data.contact.address.street if event.data and event.data.contact and event.data.contact.address else None,
        data_contact_address_other=event.data.contact.address.other if event.data and event.data.contact and event.data.contact.address else None,
        data_contact_confirmations=event.data.contact.confirmations if event.data and event.data.contact else None,
        data_job_position=event.data.job.position if event.data and event.data.job else None,
        data_job_salary=event.data.job.salary if event.data and event.data.job else None,
        data_job_type=event.data.job.type if event.data and event.data.job else None,
        data_job_company_name=event.data.job.company.name if event.data and event.data.job and event.data.job.company else None,
        data_job_company_size=event.data.job.company.size if event.data and event.data.job and event.data.job.company else None,
        data_job_company_segment=event.data.job.company.segment if event.data and event.data.job and event.data.job.company else None,
        data_job_company_country=event.data.job.company.country if event.data and event.data.job and event.data.job.company else None,
        data_job_department=event.data.job.department if event.data and event.data.job else None,
        data_preferences_purchases=event.data.preferences.purchases if event.data and event.data.preferences else None,
        data_preferences_colors=event.data.preferences.colors if event.data and event.data.preferences else None,
        data_preferences_sizes=event.data.preferences.sizes if event.data and event.data.preferences else None,
        data_preferences_devices=event.data.preferences.devices if event.data and event.data.preferences else None,
        data_preferences_channels=event.data.preferences.channels if event.data and event.data.preferences else None,
        data_preferences_payments=event.data.preferences.payments if event.data and event.data.preferences else None,
        data_preferences_brands=event.data.preferences.brands if event.data and event.data.preferences else None,
        data_preferences_fragrances=event.data.preferences.fragrances if event.data and event.data.preferences else None,
        data_preferences_services=event.data.preferences.services if event.data and event.data.preferences else None,
        data_preferences_other=event.data.preferences.other if event.data and event.data.preferences else None,
        data_loyalty_codes=event.data.loyalty.codes if event.data and event.data.loyalty else None,
        data_loyalty_card_id=event.data.loyalty.card.id if event.data and event.data.loyalty and event.data.loyalty.card else None,
        data_loyalty_card_name=event.data.loyalty.card.name if event.data and event.data.loyalty and event.data.loyalty.card else None,
        data_loyalty_card_issuer=event.data.loyalty.card.issuer if event.data and event.data.loyalty and event.data.loyalty.card else None,
        data_loyalty_card_points=event.data.loyalty.card.points if event.data and event.data.loyalty and event.data.loyalty.card else None,
        data_loyalty_card_expires=event.data.loyalty.card.expires if event.data and event.data.loyalty and event.data.loyalty.card else None,
        data_message_id=event.data.message.id if event.data and event.data.message else None,
        data_message_conversation=event.data.message.conversation if event.data and event.data.message else None,
        data_message_type=event.data.message.type if event.data and event.data.message else None,
        data_message_text=event.data.message.text if event.data and event.data.message else None,
        data_message_sender=event.data.message.sender if event.data and event.data.message else None,
        data_message_recipient=event.data.message.recipient if event.data and event.data.message else None,
        data_message_status=event.data.message.status if event.data and event.data.message else None,

        data_message_error_reason=event.data.message.error.reason,
        data_message_aux=to_json(event.data.message.aux),

        data_ec_order_id=event.data.ec.order.id,
        data_ec_order_status=event.data.ec.order.status,
        data_ec_order_receivable_value=event.data.ec.order.receivable.value,
        data_ec_order_receivable_due_date=event.data.ec.order.receivable.due_date,
        data_ec_order_receivable_currency=event.data.ec.order.receivable.currency,
        data_ec_order_payable_value=event.data.ec.order.payable.value,
        data_ec_order_payable_due_date=event.data.ec.order.payable.due_date,
        data_ec_order_payable_currency=event.data.ec.order.payable.currency,
        data_ec_order_income_value=event.data.ec.order.income.value,
        data_ec_order_income_due_date=event.data.ec.order.income.due_date,
        data_ec_order_income_currency=event.data.ec.order.income.currency,
        data_ec_order_cost_value=event.data.ec.order.cost.value,
        data_ec_order_cost_due_date=event.data.ec.order.cost.due_date,
        data_ec_order_cost_currency=event.data.ec.order.cost.currency,
        data_ec_order_affiliation=event.data.ec.order.affiliation,

        data_ec_checkout_id=event.data.ec.checkout.id,
        data_ec_checkout_status=event.data.ec.checkout.status,
        data_ec_checkout_currency=event.data.ec.checkout.currency,
        data_ec_checkout_value=event.data.ec.checkout.value,

        data_ec_product_id=event.data.ec.product.id,
        data_ec_product_name=event.data.ec.product.name,
        data_ec_product_sku=event.data.ec.product.sku,
        data_ec_product_category=event.data.ec.product.category,
        data_ec_product_brand=event.data.ec.product.brand,
        data_ec_product_variant_name=event.data.ec.product.variant.name,
        data_ec_product_variant_color=event.data.ec.product.variant.color,
        data_ec_product_variant_size=event.data.ec.product.variant.size,
        data_ec_product_price=event.data.ec.product.price,
        data_ec_product_quantity=event.data.ec.product.quantity,
        data_ec_product_position=event.data.ec.product.position,
        data_ec_product_review=event.data.ec.product.review,
        data_ec_product_rate=event.data.ec.product.rate,

        data_payment_method=event.data.payment.method,
        data_payment_credit_card_number=event.data.payment.credit_card.number,
        data_payment_credit_card_expires=event.data.payment.credit_card.expires,
        data_payment_credit_card_holder=event.data.payment.credit_card.holder,

        data_journey_state=event.data.journey.state,
        data_journey_rate=event.data.journey.rate,

        data_marketing_coupon=event.data.marketing.coupon,
        data_marketing_channel=event.data.marketing.channel,
        data_marketing_promotion_id=event.data.marketing.promotion.id,
        data_marketing_promotion_name=event.data.marketing.promotion.name,

        tags_values=event.tags.values,
        tags_count=event.tags.count,

        journey_state=event.journey.state,

        production=event.operation.production
    )


def map_to_event(event_table: EventTable) -> Event:
    return Event(
        id=event_table.id,
        name=event_table.name,
        metadata=EventMetadata(
            aux=event_table.metadata_aux,
            time=EventTime(
                insert=event_table.metadata_time_insert,
                create=event_table.metadata_time_create,
                process_time=event_table.metadata_time_process_time,
                total_time=event_table.metadata_time_total_time
            ),
            status=event_table.metadata_status,
            channel=event_table.metadata_channel,
            ip=event_table.metadata_ip,
            profile_less=event_table.metadata_profile_less,
            valid=event_table.metadata_valid,
            warning=event_table.metadata_warning,
            error=event_table.metadata_error,
            merge=event_table.metadata_merge,
            instance=Entity(id=event_table.metadata_instance_id),
            debug=event_table.metadata_debug
        ),
        type=event_table.type,
        request=event_table.request,

        source=Entity(id=event_table.source_id),
        device=Device(
            name=event_table.device_name,
            brand=event_table.device_brand,
            model=event_table.device_model,
            ip=event_table.device_ip,
            type=event_table.device_type,
            touch=event_table.device_touch,
            resolution=event_table.device_resolution,
            color_depth=event_table.device_color_depth,
            orientation=event_table.device_orientation,
            geo=Geo(
                country=Country(name=event_table.device_geo_country_name,code=event_table.device_geo_country_code),
                county=event_table.device_geo_county,
                city=event_table.device_geo_city,
                latitude=event_table.device_geo_latitude,
                longitude=event_table.device_geo_longitude,
                location=event_table.device_geo_location,
                postal=event_table.device_geo_postal
            )
        ),
        os=OS(
            name=event_table.os_name,
            version=event_table.os_version
        ),
        app=Application(
            type=event_table.app_type,
            bot=event_table.app_bot,
            name=event_table.app_name,
            version=event_table.app_version,
            language=event_table.app_language,
            resolution=event_table.app_resolution
        ),
        hit=Hit(
            name=event_table.hit_name,
            url=event_table.hit_url,
            referer=event_table.hit_referer,
            query=event_table.hit_query,
            category=event_table.hit_category
        ),
        utm=UTM(
            source=event_table.utm_source,
            medium=event_table.utm_medium,
            campaign=event_table.utm_campaign,
            term=event_table.utm_term,
            content=event_table.utm_content
        ),
        session=EventSession(
            id=event_table.session_id,
            start=event_table.session_start,
            duration=event_table.session_duration,
            tz=event_table.session_tz
        ),
        profile=PrimaryEntity(id=event_table.profile_id),
        entity=Entity(id=event_table.entity_id),
        aux=event_table.aux,
        trash=event_table.trash,
        config=event_table.config,
        context=event_table.context,
        properties=event_table.properties,
        traits=event_table.traits,

        data=EventData(
            media=ProfileMedia(
                image=event_table.data_media_image,
                webpage=event_table.data_media_webpage,
                social=ProfileSocialMedia(
                    twitter=event_table.data_media_social_twitter,
                    facebook=event_table.data_media_social_facebook,
                    youtube=event_table.data_media_social_youtube,
                    instagram=event_table.data_media_social_instagram,
                    tiktok=event_table.data_media_social_tiktok,
                    linkedin=event_table.data_media_social_linkedin,
                    reddit=event_table.data_media_social_reddit,
                    other=event_table.data_media_social_other
                )
            ),
            pii=ProfilePII(
                firstname=event_table.data_pii_firstname,
                lastname=event_table.data_pii_lastname,
                display_name=event_table.data_pii_display_name,
                birthday=event_table.data_pii_birthday,
                language=ProfileLanguage(native=event_table.data_pii_language_native, spoken=event_table.data_pii_language_spoken),
                gender=event_table.data_pii_gender,
                education=ProfileEducation(level=event_table.data_pii_education_level),
                civil=ProfileCivilData(status=event_table.data_pii_civil_status),
                attributes=ProfileAttribute(
                    height=event_table.data_pii_attributes_height,
                    weight=event_table.data_pii_attributes_weight,
                    shoe_number=event_table.data_pii_attributes_shoe_number
                )
            ),
            identifier=ProfileIdentifier(
                id=event_table.data_identifier_id,
                pk=event_table.data_identifier_pk,
                badge=event_table.data_identifier_badge,
                passport=event_table.data_identifier_passport,
                credit_card=event_table.data_identifier_credit_card,
                token=event_table.data_identifier_token,
                coupons=event_table.data_identifier_coupons
            ),
            contact=ProfileContact(
                email=ProfileEmail(
                    main=event_table.data_contact_email_main,
                    private=event_table.data_contact_email_private,
                    business=event_table.data_contact_email_business
                ),
                phone=ProfilePhone(
                    main=event_table.data_contact_phone_main,
                    business=event_table.data_contact_phone_business,
                    mobile=event_table.data_contact_phone_mobile,
                    whatsapp=event_table.data_contact_phone_whatsapp
                ),
                app=ProfileContactApp(
                    whatsapp=event_table.data_contact_app_whatsapp,
                    discord=event_table.data_contact_app_discord,
                    slack=event_table.data_contact_app_slack,
                    twitter=event_table.data_contact_app_twitter,
                    telegram=event_table.data_contact_app_telegram,
                    wechat=event_table.data_contact_app_wechat,
                    viber=event_table.data_contact_app_viber,
                    signal=event_table.data_contact_app_signal,
                    other=event_table.data_contact_app_other
                ),
                address=ProfileContactAddress(
                    town=event_table.data_contact_address_town,
                    county=event_table.data_contact_address_county,
                    country=event_table.data_contact_address_country,
                    postcode=event_table.data_contact_address_postcode,
                    street=event_table.data_contact_address_street,
                    other=event_table.data_contact_address_other
                ),
                confirmations=event_table.data_contact_confirmations
            ),
            job=ProfileJob(
                position=event_table.data_job_position,
                salary=event_table.data_job_salary,
                type=event_table.data_job_type,
                company=ProfileCompany(
                    name=event_table.data_job_company_name,
                    size=event_table.data_job_company_size,
                    segment=event_table.data_job_company_segment,
                    country=event_table.data_job_company_country
                ),
                department=event_table.data_job_department
            ),
            preferences=ProfilePreference(
                purchases=event_table.data_preferences_purchases,
                colors=event_table.data_preferences_colors,
                sizes=event_table.data_preferences_sizes,
                devices=event_table.data_preferences_devices,
                channels=event_table.data_preferences_channels,
                payments=event_table.data_preferences_payments,
                brands=event_table.data_preferences_brands,
                fragrances=event_table.data_preferences_fragrances,
                services=event_table.data_preferences_services,
                other=event_table.data_preferences_other
            ),
            loyalty=ProfileLoyalty(
                codes=event_table.data_loyalty_codes,
                card=ProfileLoyaltyCard(
                    id=event_table.data_loyalty_card_id,
                    name=event_table.data_loyalty_card_name,
                    issuer=event_table.data_loyalty_card_issuer,
                    points=event_table.data_loyalty_card_points,
                    expires=event_table.data_loyalty_card_expires
                )
            ),
            ec=EventEc(
                product=EventProduct(
                    id=event_table.data_ec_product_id,
                    name=event_table.data_ec_product_name,
                    sku=event_table.data_ec_product_sku,
                    category=event_table.data_ec_product_category,
                    brand=event_table.data_ec_product_brand,
                    variant=EventProductVariant(
                        name=event_table.data_ec_product_variant_name,
                        color=event_table.data_ec_product_variant_color,
                        size=event_table.data_ec_product_variant_size
                    ),
                    price=event_table.data_ec_product_price,
                    quantity=event_table.data_ec_product_quantity,
                    position=event_table.data_ec_product_position,
                    review=event_table.data_ec_product_review,
                    rate=event_table.data_ec_product_rate
                ),
                checkout=EventCheckout(
                    id=event_table.data_ec_checkout_id,
                    status=event_table.data_ec_checkout_status,
                    currency=event_table.data_ec_checkout_currency,
                    value=event_table.data_ec_checkout_value
                ),
                order=EventOrder(
                    id=event_table.data_ec_order_id,
                    status=event_table.data_ec_order_status,
                    receivable=Money(
                        value=event_table.data_ec_order_receivable_value,
                        due_date=event_table.data_ec_order_receivable_due_date,
                        currency=event_table.data_ec_order_receivable_currency
                    ),
                    payable=Money(
                        value=event_table.data_ec_order_payable_value,
                        due_date=event_table.data_ec_order_payable_due_date,
                        currency=event_table.data_ec_order_payable_currency
                    ),
                    income=Money(
                        value=event_table.data_ec_order_income_value,
                        due_date=event_table.data_ec_order_income_due_date,
                        currency=event_table.data_ec_order_income_currency
                    ),
                    cost=Money(
                        value=event_table.data_ec_order_cost_value,
                        due_date=event_table.data_ec_order_cost_due_date,
                        currency=event_table.data_ec_order_cost_currency
                    ),
                    affiliation=event_table.data_ec_order_affiliation
                )
            ),
            message=EventMessage(
                id=event_table.data_message_id,
                conversation=event_table.data_message_conversation,
                type=event_table.data_message_type,
                text=event_table.data_message_text,
                sender=event_table.data_message_sender,
                recipient=event_table.data_message_recipient,
                status=event_table.data_message_status,
                error_reason=event_table.data_message_error_reason,
                aux=event_table.data_message_aux
            ),
            payment=EventPayment(
                method=event_table.data_payment_method,
                credit_card=EventCreditCard(
                    number=event_table.data_payment_credit_card_number,
                    expires=event_table.data_payment_credit_card_expires,
                    holder=event_table.data_payment_credit_card_holder
                )
            ),
            marketing=EventMarketing(
                coupon=event_table.data_marketing_coupon,
                channel=event_table.data_marketing_channel,
                promotion=EventPromotion(
                    id=event_table.data_marketing_promotion_id,
                    name=event_table.data_marketing_promotion_name
                )
            )
        ),
        tags=Tags(
            values=event_table.tags_values,
            count=event_table.tags_count
        ),
        journey=EventJourney(
            state=event_table.journey_state
        ),

        production=event_table.production
    )
