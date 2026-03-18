from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    fairino_robot_ip: str = "147.175.151.23"
    fairino_rpc_port: int = 9003
    fairino_realtime_port: int = 9004
    fairino_tool: int = 0
    fairino_user: int = 0
    fairino_default_vel: float = 10.0
    fairino_dry_run: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
