"use client"

import React, { useEffect, useActionState } from "react"
import { useMarket } from "@lib/hooks/use-market"
import Input from "@modules/common/components/input"
import AccountInfo from "../account-info"
import { HttpTypes } from "@medusajs/types"
import { toast } from "@medusajs/ui"

type MyInformationProps = {
  customer: HttpTypes.StoreCustomer
}

const ProfilePassword: React.FC<MyInformationProps> = ({ customer }) => {
  const market = useMarket()
  const [successState, setSuccessState] = React.useState(false)

  // TODO: Add support for password updates
  const updatePassword = async () => {
    toast.info(
      market.code === "ru"
        ? "Обновление пароля пока не реализовано"
        : "Password update is not implemented"
    )
  }

  const clearState = () => {
    setSuccessState(false)
  }

  return (
    <form
      action={updatePassword}
      onReset={() => clearState()}
      className="w-full"
    >
      <AccountInfo
        label={market.code === "ru" ? "Пароль" : "Password"}
        currentInfo={
          <span>
            {market.code === "ru"
              ? "Пароль скрыт из соображений безопасности"
              : "The password is not shown for security reasons"}
          </span>
        }
        isSuccess={successState}
        isError={false}
        errorMessage={undefined}
        clearState={clearState}
        data-testid="account-password-editor"
      >
        <div className="grid grid-cols-2 gap-4">
          <Input
            label={market.code === "ru" ? "Текущий пароль" : "Old password"}
            name="old_password"
            required
            type="password"
            data-testid="old-password-input"
          />
          <Input
            label={market.code === "ru" ? "Новый пароль" : "New password"}
            type="password"
            name="new_password"
            required
            data-testid="new-password-input"
          />
          <Input
            label={
              market.code === "ru" ? "Подтвердите пароль" : "Confirm password"
            }
            type="password"
            name="confirm_password"
            required
            data-testid="confirm-password-input"
          />
        </div>
      </AccountInfo>
    </form>
  )
}

export default ProfilePassword
