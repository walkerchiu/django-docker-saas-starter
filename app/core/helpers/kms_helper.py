import base64

from django.conf import settings

import boto3


class KMSHelper:
    def __init__(
        self,
        key_id: str = settings.AWS_KMS_KEY_ID,
        key_id_hmac: str = settings.AWS_KMS_KEY_ID_HMAC,
        region_name: str = settings.AWS_KMS_REGION_NAME,
    ):
        self.key_id = key_id
        self.key_id_hmac = key_id_hmac
        self.client = boto3.client("kms", region_name=region_name)

    def encrypt(
        self, plaintext: str, encryption_context: dict, key_id: str = None
    ) -> str:
        if key_id is None:
            key_id = self.key_id

        response = self.client.encrypt(
            KeyId=key_id,
            Plaintext=plaintext.encode("utf-8"),
            EncryptionContext=encryption_context,
        )
        ciphertext = base64.b64encode(response["CiphertextBlob"]).decode("utf-8")

        return ciphertext

    def decrypt(
        self, ciphertext: str, encryption_context: dict, key_id: str = None
    ) -> str:
        if key_id is None:
            key_id = self.key_id

        decoded_ciphertext = base64.b64decode(ciphertext)
        response = self.client.decrypt(
            KeyId=key_id,
            CiphertextBlob=decoded_ciphertext,
            EncryptionContext=encryption_context,
        )
        plaintext = response["Plaintext"].decode("utf-8")

        return plaintext

    def generate_hmac(
        self, plaintext: str, algorithm: str = "HMAC_SHA_256", key_id: str = None
    ) -> str:
        if key_id is None:
            key_id = self.key_id_hmac

        response = self.client.generate_mac(
            KeyId=key_id,
            Message=plaintext.encode("utf-8"),
            MacAlgorithm=algorithm,
        )
        hmac = base64.b64encode(response["Mac"]).decode("utf-8")

        return hmac
