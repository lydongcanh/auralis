from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


class AnsaradaApi:

    BASE_URL = "https://api.dev1.ansarada.com/v1/graphql"

    async def get_data_rooms_async(self, access_token: str, first: int = 10):
        transport = AIOHTTPTransport(url=self.BASE_URL, headers={"Authorization": f"Bearer {access_token}"})
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql(f"""
            query {{
                me {{
                    dataRoomUsers(first: {first}) {{
                        nodes {{
                            dataRoom {{
                                id
                                displayName
                            }}
                        }}
                    }}
                }}
            }}
        """)

        return await client.execute_async(query)